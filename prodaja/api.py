"""Endpoints for quote estimation and work-order conversion."""

from __future__ import annotations

import hashlib
import hmac
import json
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from tenants.models import Tenant, TenantUser

from .models.quote import EstimSnapshot, Quote, QuoteRevision
from .services.convert_to_wo import convert_to_work_order
from .services.estimator.dto import ItemInput, QuoteInput
from .services.estimator.engine import estimate


class IsTenantUser(BasePermission):
    """Allow access to authenticated users bound to the request tenant."""

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return TenantUser.objects.filter(
            tenant__name=request.tenant,
            user=request.user,
            role__in=["owner", "manager", "staff"],
        ).exists()


_IDEMPOTENCY_CACHE: dict[tuple[str, str, str, str], dict[str, Any]] = {}


def _cache_key(request, extra: str = "") -> tuple[str, str, str, str]:
    return (
        request.tenant,
        request.path,
        request.META.get("HTTP_IDEMPOTENCY_KEY", ""),
        extra,
    )


def _get_tenant(request) -> Tenant:
    return Tenant.objects.get(name=request.tenant)


def _parse_quote_input(data: dict) -> QuoteInput:
    items = [ItemInput(**item) for item in data.get("items", [])]
    return QuoteInput(
        tenant=data["tenant"],
        currency=data["currency"],
        vat_rate=Decimal(str(data["vat_rate"])),
        is_vat_registered=data["is_vat_registered"],
        risk_band=data["risk_band"],
        contingency_pct=Decimal(str(data["contingency_pct"])),
        margin_target_pct=Decimal(str(data["margin_target_pct"])),
        items=items,
        options=data["options"],
    )


def _serialize_breakdowns(breakdowns: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    out: dict[str, Any] = {}
    assumptions: dict[str, Any] = {}
    for opt, bd in breakdowns.items():
        out[opt] = {
            **{k: float(v) for k, v in bd.components.items()},
            "contingency": float(bd.contingency),
            "margin": float(bd.margin),
            "net_total": float(bd.net_total),
            "vat_total": float(bd.vat_total),
            "gross_total": float(bd.gross_total),
        }
        assumptions = bd.assumptions
    return out, assumptions


def _snapshot_dict(snapshot: EstimSnapshot) -> dict[str, Any]:
    return {
        "input": snapshot.input_data,
        "breakdown": snapshot.breakdown,
        "norms_version": snapshot.norms_version,
        "price_list_version": snapshot.price_list_version,
        "rounding_policy": snapshot.rounding_policy,
    }


def _compute_hash(snapshot_data: dict) -> str:
    payload = json.dumps(snapshot_data, sort_keys=True)
    return hmac.new(settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()


class EstimateView(APIView):
    permission_classes = [IsTenantUser]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "estimate"

    def post(self, request):
        if "HTTP_IDEMPOTENCY_KEY" not in request.META:
            return Response({"detail": "Missing Idempotency-Key"}, status=400)
        key = _cache_key(request)
        if key in _IDEMPOTENCY_CACHE:
            return Response(_IDEMPOTENCY_CACHE[key])
        quote_input = _parse_quote_input(request.data)
        breakdowns = estimate(quote_input)
        serialized, assumptions = _serialize_breakdowns(breakdowns)
        resp = {"options": serialized, "assumptions": assumptions}
        _IDEMPOTENCY_CACHE[key] = resp
        return Response(resp)


class QuoteCreateView(APIView):
    permission_classes = [IsTenantUser]

    def post(self, request):
        tenant_obj = _get_tenant(request)
        quote_input = _parse_quote_input(request.data)
        breakdowns = estimate(quote_input)
        serialized, assumptions = _serialize_breakdowns(breakdowns)
        quote = Quote.objects.create(
            tenant=tenant_obj,
            number=request.data.get("number"),
            valid_until=request.data.get("valid_until"),
            currency=quote_input.currency,
            vat_rate=quote_input.vat_rate,
            is_vat_registered=quote_input.is_vat_registered,
            customer_name=request.data.get("customer_name", ""),
            risk_band=quote_input.risk_band,
            contingency_pct=quote_input.contingency_pct,
            margin_target_pct=quote_input.margin_target_pct,
        )
        EstimSnapshot.objects.create(
            tenant=tenant_obj,
            quote=quote,
            norms_version=assumptions.get("norms_version", ""),
            price_list_version=assumptions.get("price_list_version", ""),
            rounding_policy=assumptions.get("rounding_policy", ""),
            input_data=request.data,
            breakdown=serialized,
            version="1",
        )
        return Response({"id": quote.id, "status": quote.status}, status=status.HTTP_201_CREATED)


class QuoteDetailView(APIView):
    permission_classes = [IsTenantUser]

    def get(self, request, pk: int):
        tenant_obj = _get_tenant(request)
        quote = get_object_or_404(Quote, pk=pk, tenant=tenant_obj)
        snapshot = quote.snapshots.order_by("-created_at").first()
        data = {
            "id": quote.id,
            "number": quote.number,
            "status": quote.status,
            "snapshot": _snapshot_dict(snapshot) if snapshot else None,
        }
        return Response(data)


class QuoteSendView(APIView):
    permission_classes = [IsTenantUser]

    def post(self, request, pk: int):
        tenant_obj = _get_tenant(request)
        quote = get_object_or_404(Quote, pk=pk, tenant=tenant_obj)
        quote.status = "sent"
        quote.save()
        return Response({"status": quote.status})


class QuoteAcceptView(APIView):
    permission_classes = [IsTenantUser]

    def post(self, request, pk: int):
        if "HTTP_IDEMPOTENCY_KEY" not in request.META:
            return Response({"detail": "Missing Idempotency-Key"}, status=400)
        key = _cache_key(request, extra=str(pk))
        if key in _IDEMPOTENCY_CACHE:
            return Response(_IDEMPOTENCY_CACHE[key])
        tenant_obj = _get_tenant(request)
        quote = get_object_or_404(Quote, pk=pk, tenant=tenant_obj)
        snapshot = quote.snapshots.order_by("-created_at").first()
        if not snapshot:
            return Response({"detail": "No snapshot"}, status=400)
        snapshot_data = _snapshot_dict(snapshot)
        expected = _compute_hash(snapshot_data)
        provided = request.data.get("acceptance_hash")
        if expected != provided:
            return Response({"detail": "Invalid acceptance hash"}, status=400)
        if quote.status != "accepted":
            quote.status = "accepted"
            quote.accepted_at = timezone.now()
            quote.acceptance_hash = expected
            quote.save()
        resp = {
            "status": quote.status,
            "accepted_at": quote.accepted_at.isoformat() if quote.accepted_at else None,
        }
        _IDEMPOTENCY_CACHE[key] = resp
        return Response(resp)


class QuoteToWOView(APIView):
    permission_classes = [IsTenantUser]

    def post(self, request, pk: int):
        tenant_obj = _get_tenant(request)
        option = request.data.get("option")
        if not option:
            return Response({"detail": "option required"}, status=400)
        wo = convert_to_work_order(tenant_obj, pk, option)
        return Response({"work_order_id": wo.id})

        # conversion to work order completed


class QuoteRevisionView(APIView):
    permission_classes = [IsTenantUser]

    def post(self, request, pk: int):
        tenant_obj = _get_tenant(request)
        quote = get_object_or_404(Quote, pk=pk, tenant=tenant_obj)
        input_data = request.data.get("input")
        if not input_data:
            return Response({"detail": "input required"}, status=400)
        reason = request.data.get("reason_code", "")
        delta = request.data.get("delta", {})
        quote_input = _parse_quote_input(input_data)
        breakdowns = estimate(quote_input)
        serialized, assumptions = _serialize_breakdowns(breakdowns)
        prev_snapshot = quote.snapshots.order_by("-created_at").first()
        new_version = str(quote.revision + 1)
        new_snapshot = EstimSnapshot.objects.create(
            tenant=tenant_obj,
            quote=quote,
            norms_version=assumptions.get("norms_version", ""),
            price_list_version=assumptions.get("price_list_version", ""),
            rounding_policy=assumptions.get("rounding_policy", ""),
            input_data=input_data,
            breakdown=serialized,
            version=new_version,
        )
        QuoteRevision.objects.create(
            tenant=tenant_obj,
            parent=quote,
            prev_snapshot=prev_snapshot,
            new_snapshot=new_snapshot,
            reason_code=reason,
            delta=delta,
        )
        quote.revision += 1
        quote.save()
        return Response({"revision": quote.revision})
