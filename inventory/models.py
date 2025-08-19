from __future__ import annotations
from decimal import Decimal
from django.db import models, transaction
from django.utils import timezone
from tenants.models import Tenant
from financije.ledger import post_entry


class UoM(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    ratio_to_base = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal('1'))

    def __str__(self):
        return self.code


class Item(models.Model):
    MATERIAL = 'material'
    CONSUMABLE = 'consumable'
    PAINT = 'paint'
    SEMI = 'semi'
    SERVICE = 'service'
    ITEM_TYPES = [
        (MATERIAL, 'Material'),
        (CONSUMABLE, 'Consumable'),
        (PAINT, 'Paint'),
        (SEMI, 'Semi-finished'),
        (SERVICE, 'Service'),
    ]

    sku = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=120)
    uom_base = models.ForeignKey(UoM, on_delete=models.PROTECT, related_name='base_items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    has_lots = models.BooleanField(default=False)
    shelf_life_days = models.PositiveIntegerField(null=True, blank=True)
    track_length = models.BooleanField(default=False)
    direct_expense_account = models.CharField(max_length=10, null=True, blank=True)  # 6xx overhead skip WIP
    is_paint_component = models.BooleanField(default=False)

    def __str__(self):
        return self.sku


class Warehouse(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.code


class Location(models.Model):
    BIN = 'bin'
    STAGING = 'staging'
    WIP = 'wip'
    SCRAP = 'scrap'
    TYPES = [
        (BIN, 'Bin'),
        (STAGING, 'Staging'),
        (WIP, 'WIP'),
        (SCRAP, 'Scrap'),
    ]
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    code = models.CharField(max_length=30)
    type = models.CharField(max_length=10, choices=TYPES, default=BIN)

    class Meta:
        unique_together = ('warehouse', 'code')

    def __str__(self):
        return f"{self.warehouse.code}:{self.code}"


class StockLot(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    lot_code = models.CharField(max_length=40)
    expiry = models.DateField(null=True, blank=True)
    attrs = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('item', 'lot_code')

    def __str__(self):
        return f"{self.item.sku}:{self.lot_code}"


class StockQuant(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    lot = models.ForeignKey(StockLot, on_delete=models.CASCADE, null=True, blank=True)
    qty = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal('0'))
    cost_per_uom = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal('0'))

    class Meta:
        unique_together = ('item', 'warehouse', 'location', 'lot')


class StockMove(models.Model):  # WorkOrder defined later; forward ref used
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    ts = models.DateTimeField(default=timezone.now)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, null=True, blank=True)
    uom = models.ForeignKey(UoM, on_delete=models.PROTECT, null=True, blank=True)
    qty = models.DecimalField(max_digits=18, decimal_places=6)
    src = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='moves_out', null=True, blank=True)
    dst = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='moves_in', null=True, blank=True)
    lot = models.ForeignKey(StockLot, on_delete=models.PROTECT, null=True, blank=True)
    ref = models.CharField(max_length=60)
    kind = models.CharField(max_length=30, default='generic')  # receive, issue_wip, return_wip, scrap_wip, finish_wip
    work_order = models.ForeignKey('WorkOrder', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_moves')
    price_unit = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal('0'))
    value = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal('0'))
    state = models.CharField(max_length=12, default='done')

    class Meta:
        indexes = [models.Index(fields=['ref', 'tenant'])]
        constraints = [
            models.UniqueConstraint(fields=['tenant', 'ref'], name='inventory_unique_ref_per_tenant')
        ]


class WorkOrder(models.Model):  # stock_moves reverse relation referenced in StockMove
    code = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, default='open')  # open, finished
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.code


class WorkOrderReservation(models.Model):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='reservations')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    qty = models.DecimalField(max_digits=18, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=120, blank=True)

    class Meta:
        indexes = [models.Index(fields=['work_order', 'item'])]
        unique_together = ('work_order', 'item', 'note')  # note can differentiate phases


def reserve_for_work_order(*, work_order: WorkOrder, item: Item, qty: Decimal, note: str = ""):
    if qty <= 0:
        raise ValueError("qty must be > 0")
    return WorkOrderReservation.objects.create(work_order=work_order, item=item, qty=qty, note=note)


# Minimal WAC receive helper (will expand in next PRs)

def receive_inventory(*, tenant: Tenant, item: Item, warehouse: Warehouse, location: Location, qty: Decimal, price_per_uom: Decimal, ref: str, lot_code: str | None = None, expiry=None):
    # Weighted average cost update on quant (item+wh aggregated by location for now)
    lot = None
    if lot_code:
        lot, _ = StockLot.objects.get_or_create(item=item, lot_code=lot_code, defaults={'expiry': expiry})
    quant, _ = StockQuant.objects.get_or_create(item=item, warehouse=warehouse, location=location, lot=lot, defaults={'qty': 0, 'cost_per_uom': 0})
    old_qty = quant.qty
    old_cost = quant.cost_per_uom
    new_qty = old_qty + qty
    if new_qty == 0:
        avg = Decimal('0')
    elif old_qty == 0:
        avg = price_per_uom
    else:
        avg = (old_qty * old_cost + qty * price_per_uom) / new_qty
    quant.qty = new_qty
    quant.cost_per_uom = avg
    quant.save(update_fields=['qty', 'cost_per_uom'])
    move = StockMove.objects.create(tenant=tenant, item=item, uom=item.uom_base, qty=qty, src=None, dst=location, ref=ref, price_unit=price_per_uom, value=qty * price_per_uom, lot=lot, kind='receive')
    # GL posting (DR 140 inventory / CR 220 AP simplified; ignoring tax for MVP)
    post_entry(
        tenant=tenant,
        ref=f"INV-{ref}",
        kind='inventory_receive',
        memo=f"Receive {item.sku} {qty}",
        lines=[
            {"account": "140", "dc": "D", "amount": move.value},
            {"account": "220", "dc": "C", "amount": move.value},
        ],
    )
    return move, quant


def _get_quant(item: Item, warehouse: Warehouse, location: Location, lot=None):
    return StockQuant.objects.get_or_create(
        item=item,
        warehouse=warehouse,
        location=location,
        lot=lot,
        defaults={"qty": Decimal("0"), "cost_per_uom": Decimal("0")},
    )[0]


def _find_quant_for_issue(item: Item, warehouse: Warehouse, location: Location, needed: Decimal):
    # Try exact lot-less quant first
    q = StockQuant.objects.filter(item=item, warehouse=warehouse, location=location).order_by('lot_id').first()
    if q and q.qty >= needed:
        return q
    # Fallback: iterate all quants and pick one with enough qty
    for q in StockQuant.objects.filter(item=item, warehouse=warehouse, location=location).order_by('lot_id'):
        if q.qty >= needed:
            return q
    # If total across lots sufficient, allow spanning (simplify: not implemented yet)
    total = sum(q.qty for q in StockQuant.objects.filter(item=item, warehouse=warehouse, location=location))
    if total >= needed:
        # Just use first and allow negative? For MVP raise instructing to specify lot.
        raise ValueError('Multi-lot consumption not implemented; specify lot for partial lot usage')
    return None


def issue_to_wip(*, tenant: Tenant, item: Item, warehouse: Warehouse, src: Location, wip: Location, qty: Decimal, ref: str, work_order: 'WorkOrder | None' = None, lot: StockLot | None = None):
    if qty <= 0:
        raise ValueError("qty must be > 0")
    if wip.type != Location.WIP:
        raise ValueError("Destination must be WIP location")
    # Idempotency guard
    existing = StockMove.objects.filter(tenant=tenant, ref=ref).first()
    if existing:
        return existing, _get_quant(item, warehouse, src), _get_quant(item, warehouse, wip)
    if lot:
        src_q = _get_quant(item, warehouse, src, lot)
    else:
        src_q = _find_quant_for_issue(item, warehouse, src, qty)
        if not src_q:
            raise ValueError("Insufficient stock to issue")
    if src_q.qty < qty:
        raise ValueError("Insufficient stock to issue")
    unit_cost = src_q.cost_per_uom
    value = unit_cost * qty
    # Adjust source
    src_q.qty -= qty
    src_q.save(update_fields=["qty"])
    # Add to WIP (average cost is passthrough)
    wip_q = _get_quant(item, warehouse, wip)
    # If wip_q.qty == 0 keep cost_per_uom same, else ensure it matches (weighted avg among same unit cost)
    if wip_q.qty == 0:
        wip_q.cost_per_uom = unit_cost
    # If existing different cost, compute blended WIP cost (rare before finish)
    if wip_q.qty and wip_q.cost_per_uom != unit_cost:
        wip_q.cost_per_uom = (wip_q.qty * wip_q.cost_per_uom + qty * unit_cost) / (wip_q.qty + qty)
    wip_q.qty += qty
    wip_q.save(update_fields=["qty", "cost_per_uom"])
    move = StockMove.objects.create(
        tenant=tenant,
        item=item,
        uom=item.uom_base,
        qty=qty,
        src=src,
        dst=wip,
        ref=ref,
        kind='issue_wip',
        work_order=work_order,
        price_unit=unit_cost,
        value=value,
        lot=lot,
    )
    # GL: DR 150 / CR 140
    post_entry(
        tenant=tenant,
        ref=f"ISS-{ref}",
        kind="inventory_issue_wip",
        memo=f"Issue {item.sku} {qty} to WIP",
        lines=[
            {"account": "150", "dc": "D", "amount": value},
            {"account": "140", "dc": "C", "amount": value},
        ],
    )
    return move, src_q, wip_q


def return_from_wip(*, tenant: Tenant, item: Item, warehouse: Warehouse, wip: Location, dst: Location, qty: Decimal, ref: str, work_order: 'WorkOrder | None' = None):
    if qty <= 0:
        raise ValueError("qty must be > 0")
    if wip.type != Location.WIP:
        raise ValueError("Source must be WIP location")
    existing = StockMove.objects.filter(tenant=tenant, ref=ref).first()
    if existing:
        return existing, _get_quant(item, warehouse, dst), _get_quant(item, warehouse, wip)
    wip_q = _get_quant(item, warehouse, wip)
    if wip_q.qty < qty:
        raise ValueError("Insufficient WIP stock to return")
    unit_cost = wip_q.cost_per_uom
    value = unit_cost * qty
    # Deduct from WIP
    wip_q.qty -= qty
    wip_q.save(update_fields=["qty"])
    # Add back to destination (weighted avg update like receive)
    dst_q = _get_quant(item, warehouse, dst)
    old_qty = dst_q.qty
    old_cost = dst_q.cost_per_uom
    new_qty = old_qty + qty
    if new_qty == 0:
        new_cost = Decimal("0")
    elif old_qty == 0:
        new_cost = unit_cost
    else:
        new_cost = (old_qty * old_cost + qty * unit_cost) / new_qty
    dst_q.qty = new_qty
    dst_q.cost_per_uom = new_cost
    dst_q.save(update_fields=["qty", "cost_per_uom"])
    move = StockMove.objects.create(
        tenant=tenant,
        item=item,
        uom=item.uom_base,
        qty=qty,
        src=wip,
        dst=dst,
        ref=ref,
        kind='return_wip',
        work_order=work_order,
        price_unit=unit_cost,
        value=value,
    )
    # GL: DR 140 / CR 150
    post_entry(
        tenant=tenant,
        ref=f"RET-{ref}",
        kind="inventory_return_wip",
        memo=f"Return {item.sku} {qty} from WIP",
        lines=[
            {"account": "140", "dc": "D", "amount": value},
            {"account": "150", "dc": "C", "amount": value},
        ],
    )
    return move, dst_q, wip_q


def scrap_from_wip(*, tenant: Tenant, item: Item, warehouse: Warehouse, wip: Location, scrap_loc: Location, qty: Decimal, ref: str, work_order: 'WorkOrder | None' = None):
    if qty <= 0:
        raise ValueError("qty must be > 0")
    if wip.type != Location.WIP:
        raise ValueError("Source must be WIP location")
    if scrap_loc.type != Location.SCRAP:
        raise ValueError("Destination must be SCRAP location")
    existing = StockMove.objects.filter(tenant=tenant, ref=ref).first()
    if existing:
        return existing, _get_quant(item, warehouse, wip)
    wip_q = _get_quant(item, warehouse, wip)
    if wip_q.qty < qty:
        raise ValueError("Insufficient WIP stock to scrap")
    unit_cost = wip_q.cost_per_uom
    value = unit_cost * qty
    # Deduct from WIP
    wip_q.qty -= qty
    wip_q.save(update_fields=["qty"])
    move = StockMove.objects.create(
        tenant=tenant,
        item=item,
        uom=item.uom_base,
        qty=qty,
        src=wip,
        dst=scrap_loc,
        ref=ref,
        kind='scrap_wip',
        work_order=work_order,
        price_unit=unit_cost,
        value=value,
    )
    # GL: DR 699 / CR 150
    post_entry(
        tenant=tenant,
        ref=f"SCR-{ref}",
        kind="inventory_scrap_wip",
        memo=f"Scrap {item.sku} {qty} from WIP",
        lines=[
            {"account": "699", "dc": "D", "amount": value},
            {"account": "150", "dc": "C", "amount": value},
        ],
    )
    return move, wip_q


@transaction.atomic
def finish_work_order(*, tenant: Tenant, work_order: WorkOrder, ref: str):
    if work_order.status == 'finished':
        # Idempotent: if finished, just return existing finishing move if any
        existing = StockMove.objects.filter(tenant=tenant, ref=ref).first()
        if existing:
            return existing
        raise ValueError('Work order already finished')
    # Sum remaining WIP value for this work order by aggregating issue/return/scrap moves
    moves = StockMove.objects.filter(work_order=work_order, tenant=tenant)
    issue_val = sum(m.value for m in moves if m.kind == 'issue_wip')
    return_val = sum(m.value for m in moves if m.kind == 'return_wip')
    scrap_val = sum(m.value for m in moves if m.kind == 'scrap_wip')
    remaining = issue_val - return_val - scrap_val
    if remaining <= 0:
        remaining = Decimal('0')
    # Create GL entry only if remaining > 0
    if remaining > 0:
        post_entry(
            tenant=tenant,
            ref=f"FIN-{ref}",
            kind='inventory_finish_wip',
            memo=f"Finish WO {work_order.code}",
            lines=[
                {"account": "500", "dc": "D", "amount": remaining},
                {"account": "150", "dc": "C", "amount": remaining},
            ],
        )
    move = StockMove.objects.create(
        tenant=tenant,
        item=None,
        uom=None,
        qty=Decimal('0'),
        src=None,
        dst=None,
        ref=ref,
        kind='finish_wip',
        price_unit=Decimal('0'),
        value=remaining,
        work_order=work_order,
    )
    work_order.status = 'finished'
    work_order.finished_at = timezone.now()
    work_order.save(update_fields=['status', 'finished_at'])
    return move


class CutPlan(models.Model):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='cut_plans')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    bar_length_m = models.DecimalField(max_digits=18, decimal_places=6)
    cuts = models.JSONField(default=list)  # list of segment lengths m
    offcuts = models.JSONField(default=list)  # list of remaining piece lengths
    created_at = models.DateTimeField(auto_now_add=True)
    ref = models.CharField(max_length=60, unique=True)


def execute_cut_plan(*, tenant: Tenant, work_order: WorkOrder, item: Item, warehouse: Warehouse, src: Location, wip: Location, plan_ref: str, cuts: list[Decimal], bar_length: Decimal | None = None):
    total_cut: Decimal = sum((Decimal(c) for c in cuts), Decimal('0'))
    src_q = _get_quant(item, warehouse, src)
    if src_q.qty < total_cut:
        raise ValueError('Insufficient length stock for cut plan')
    # Issue only consumed length
    issue_to_wip(tenant=tenant, item=item, warehouse=warehouse, src=src, wip=wip, qty=Decimal(total_cut), ref=f'CUT-{plan_ref}', work_order=work_order)
    leftover = Decimal('0')
    if item.track_length and bar_length:
        if bar_length < total_cut:
            raise ValueError('bar_length smaller than cuts total')
        leftover = bar_length - total_cut
    cp = CutPlan.objects.create(
        work_order=work_order,
        item=item,
        bar_length_m=bar_length or total_cut,
        cuts=[str(c) for c in cuts],
        offcuts=[str(leftover)] if leftover > 0 else [],
        ref=plan_ref,
    )
    return cp


class PaintMix(models.Model):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name='paint_mixes')
    base_item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='paintmix_base')
    qty_base = models.DecimalField(max_digits=18, decimal_places=6)
    hardener_pct = models.DecimalField(max_digits=6, decimal_places=2)
    thinner_pct = models.DecimalField(max_digits=6, decimal_places=2)
    loss_pct = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0'))
    total_mix_qty = models.DecimalField(max_digits=18, decimal_places=6)
    ref = models.CharField(max_length=60, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


def mix_paint(*, tenant: Tenant, work_order: WorkOrder, base_item: Item, qty_L: Decimal, hardener: Item, hardener_pct: Decimal, thinner: Item, thinner_pct: Decimal, loss_pct: Decimal, warehouse: Warehouse, bin_loc: Location, wip_loc: Location, ref: str):
    # Compute component quantities
    qty_hardener = (qty_L * hardener_pct / Decimal('100')).quantize(Decimal('0.000001'))
    qty_thinner = (qty_L * thinner_pct / Decimal('100')).quantize(Decimal('0.000001'))
    total_before_loss = qty_L + qty_hardener + qty_thinner
    loss_qty = (total_before_loss * loss_pct / Decimal('100')).quantize(Decimal('0.000001'))
    # Issue components
    issue_to_wip(tenant=tenant, item=base_item, warehouse=warehouse, src=bin_loc, wip=wip_loc, qty=qty_L, ref=f'{ref}-B', work_order=work_order)
    if qty_hardener > 0:
        issue_to_wip(tenant=tenant, item=hardener, warehouse=warehouse, src=bin_loc, wip=wip_loc, qty=qty_hardener, ref=f'{ref}-H', work_order=work_order)
    if qty_thinner > 0:
        issue_to_wip(tenant=tenant, item=thinner, warehouse=warehouse, src=bin_loc, wip=wip_loc, qty=qty_thinner, ref=f'{ref}-T', work_order=work_order)
    if loss_qty > 0:
        scrap_loc = Location.objects.filter(warehouse=warehouse, type=Location.SCRAP).first()
        if not scrap_loc:
            raise ValueError('Missing SCRAP location for loss booking')
        scrap_from_wip(tenant=tenant, item=base_item, warehouse=warehouse, wip=wip_loc, scrap_loc=scrap_loc, qty=loss_qty, ref=f'{ref}-L', work_order=work_order)
    mix = PaintMix.objects.create(work_order=work_order, base_item=base_item, qty_base=qty_L, hardener_pct=hardener_pct, thinner_pct=thinner_pct, loss_pct=loss_pct, total_mix_qty=total_before_loss - loss_qty, ref=ref)
    return mix


def adjust_inventory(*, tenant: Tenant, item: Item, warehouse: Warehouse, location: Location, new_qty: Decimal, ref: str, reason: str = 'count'):
    quant = _get_quant(item, warehouse, location)
    diff = new_qty - quant.qty
    if diff == 0:
        return quant
    unit_cost = quant.cost_per_uom or Decimal('0')
    value = (abs(diff) * unit_cost)
    # Update quantity
    quant.qty = new_qty
    quant.save(update_fields=['qty'])
    if diff > 0:
        # Surplus: DR 140 / CR 420 (simplify using 400 revenue placeholder if 420 absent)
        post_entry(
            tenant=tenant,
            ref=f'ADJ-{ref}',
            kind='inventory_adjust_plus',
            memo=f'Inventory surplus {item.sku}',
            lines=[
                {"account": "140", "dc": "D", "amount": value},
                {"account": "400", "dc": "C", "amount": value},
            ],
        )
    else:
        post_entry(
            tenant=tenant,
            ref=f'ADJ-{ref}',
            kind='inventory_adjust_minus',
            memo=f'Inventory shrink {item.sku}',
            lines=[
                {"account": "699", "dc": "D", "amount": value},
                {"account": "140", "dc": "C", "amount": value},
            ],
        )
    return quant
