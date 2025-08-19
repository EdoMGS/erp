"""External bank API synchronization service layer.

Separated from models so it can be mocked / replaced and to keep ORM models pure.
"""
from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # type: ignore

from financije.models.bank import BankTransaction

logger = logging.getLogger(__name__)


def _quantize(v: Decimal) -> Decimal:
    return Decimal(str(v)).quantize(Decimal("0.01"), ROUND_HALF_UP)


def sync_bank_transactions(*, api_url: str, api_key: str) -> int:
    """Fetch transactions from remote API, upsert BankTransaction rows.

    Returns number of processed (created or updated) records.
    """
    retry_strategy = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    processed = 0
    try:
        resp = session.get(api_url, headers=headers, timeout=15)
        resp.raise_for_status()
        payload = resp.json()
        for t in payload:
            referenca = t.get("reference")
            if not referenca:
                continue
            tip = t.get("type")
            iznos = _quantize(Decimal(str(t.get("amount", "0.00"))))
            opis = t.get("description", "")
            datum_trx = t.get("transaction_date")
            datum_val = t.get("value_date")
            saldo_trx = _quantize(Decimal(str(t.get("balance", "0.00"))))
            bank_acc = t.get("iban", "") or ""  # prefer empty if missing
            bank_naziv = t.get("bank_name", "")
            currency = t.get("currency", "EUR")
            obj, created = BankTransaction.objects.update_or_create(
                referenca=referenca,
                defaults={
                    "tip_transakcije": tip,
                    "iznos": iznos,
                    "opis": opis,
                    "datum": datum_trx,
                    "datum_valute": datum_val,
                    "saldo": saldo_trx,
                    "bank_account_number": bank_acc,
                    "bank_name": bank_naziv,
                    "valuta": currency,
                },
            )
            processed += 1
            logger.debug("%s bank txn %s", "Created" if created else "Updated", referenca)
        return processed
    except requests.exceptions.RequestException as e:  # pragma: no cover network error path
        logger.error("Bank sync network error: %s", e)
        raise
