import pytest
from decimal import Decimal
from tenants.models import Tenant
from inventory.models import UoM, Item, Warehouse, Location, receive_inventory, issue_to_wip, return_from_wip, scrap_from_wip, StockQuant, WorkOrder, finish_work_order, reserve_for_work_order, WorkOrderReservation
from financije.ledger import trial_balance

pytestmark = pytest.mark.django_db


def setup_basic_item():
    m = UoM.objects.create(code='M', name='Metar')
    item = Item.objects.create(sku='PROFIL-UNP80', name='U profil', uom_base=m, item_type=Item.MATERIAL, has_lots=False)
    wh = Warehouse.objects.create(code='MAIN', name='Glavno')
    bin_loc = Location.objects.create(warehouse=wh, code='A1', type=Location.BIN)
    wip_loc = Location.objects.create(warehouse=wh, code='WIP', type=Location.WIP)
    scrap_loc = Location.objects.create(warehouse=wh, code='SCR', type=Location.SCRAP)
    return item, wh, bin_loc, wip_loc, scrap_loc


def test_issue_and_return_wip_flow():
    tenant = Tenant.objects.create(name='T1')
    item, wh, bin_loc, wip_loc, scrap_loc = setup_basic_item()
    receive_inventory(tenant=tenant, item=item, warehouse=wh, location=bin_loc, qty=Decimal('10'), price_per_uom=Decimal('3'), ref='PO1')
    # Issue 6 to WIP
    issue_to_wip(tenant=tenant, item=item, warehouse=wh, src=bin_loc, wip=wip_loc, qty=Decimal('6'), ref='ISS1')
    # Return 2
    return_from_wip(tenant=tenant, item=item, warehouse=wh, wip=wip_loc, dst=bin_loc, qty=Decimal('2'), ref='RET1')
    # Scrap 1
    scrap_from_wip(tenant=tenant, item=item, warehouse=wh, wip=wip_loc, scrap_loc=scrap_loc, qty=Decimal('1'), ref='SCR1')
    # Check remaining quantities: initial 10 - issue 6 + return 2 - scrap 1 => bin 6, wip 3
    bin_q = StockQuant.objects.get(item=item, location=bin_loc)
    wip_q = StockQuant.objects.get(item=item, location=wip_loc)
    assert bin_q.qty == Decimal('6')
    assert wip_q.qty == Decimal('3')
    # Trial balance: inventory 140 should net to value of bin + wip (6+3)*3=27; WIP (150) should hold 3*3=9; scrap posted to 699 (1*3)
    tb = dict((row[0], row) for row in trial_balance(tenant, show_netted=True))
    # Extract balances
    inv_val = sum(r[3] for k, r in tb.items() if k in ('140', '150', '699'))
    assert '699' in tb  # scrap expense posted
    # Basic sanity: total debit - credit across those accounts equals 0 after internal moves except scrap expense
    # Not asserting exact numbers for now beyond presence


def test_finish_work_order_flow():
    tenant = Tenant.objects.create(name='T2')
    item, wh, bin_loc, wip_loc, scrap_loc = setup_basic_item()
    wo = WorkOrder.objects.create(code='WO-1')
    receive_inventory(tenant=tenant, item=item, warehouse=wh, location=bin_loc, qty=Decimal('10'), price_per_uom=Decimal('3'), ref='PO1')
    issue_to_wip(tenant=tenant, item=item, warehouse=wh, src=bin_loc, wip=wip_loc, qty=Decimal('6'), ref='ISS1', work_order=wo)
    scrap_from_wip(tenant=tenant, item=item, warehouse=wh, wip=wip_loc, scrap_loc=scrap_loc, qty=Decimal('1'), ref='SCR1', work_order=wo)
    # Remaining WIP value 5 * 3 = 15 -> finish posts 500/150
    finish_work_order(tenant=tenant, work_order=wo, ref='FIN1')
    assert wo.status == 'finished'
    # Idempotent: second finish returns existing move / no duplicate GL
    finish_work_order(tenant=tenant, work_order=wo, ref='FIN1')
    tb = dict((row[0], row) for row in trial_balance(tenant, show_netted=True))
    # Expect 500 (COGS) debit and 150 credit of same amount minus scrap already recognized (scrap already moved 699/150)
    assert '500' in tb
    assert '150' in tb


def test_reservation_creation():
    tenant = Tenant.objects.create(name='T3')  # tenant not used yet by reservations but aligns future multi-tenant
    item, wh, bin_loc, wip_loc, scrap_loc = setup_basic_item()
    wo = WorkOrder.objects.create(code='WO-RES')
    res = reserve_for_work_order(work_order=wo, item=item, qty=Decimal('5'))
    assert isinstance(res, WorkOrderReservation)
    assert res.qty == Decimal('5')
    assert wo.reservations.count() == 1


def test_issue_auto_multi_lot_fefo():
    tenant = Tenant.objects.create(name='T4')
    m = UoM.objects.create(code='L', name='L')
    item = Item.objects.create(sku='MLT', name='Multi', uom_base=m, item_type=Item.MATERIAL, has_lots=True)
    wh = Warehouse.objects.create(code='W1', name='W1')
    bin_loc = Location.objects.create(warehouse=wh, code='BIN', type=Location.BIN)
    wip_loc = Location.objects.create(warehouse=wh, code='WIP', type=Location.WIP)
    # Receive two lots with different expiry
    receive_inventory(tenant=tenant, item=item, warehouse=wh, location=bin_loc, qty=Decimal('5'), price_per_uom=Decimal('2'), ref='L1', lot_code='LOT1')
    receive_inventory(tenant=tenant, item=item, warehouse=wh, location=bin_loc, qty=Decimal('7'), price_per_uom=Decimal('4'), ref='L2', lot_code='LOT2')
    from inventory.models import issue_to_wip_auto, StockLot
    moves = issue_to_wip_auto(tenant=tenant, item=item, warehouse=wh, src=bin_loc, wip=wip_loc, qty=Decimal('8'), ref='AUTO1')
    assert len(moves) == 2  # spans two lots
    # First move should be from lot LOT1 consuming all 5, second from LOT2 consuming 3
    lots = [mv.lot.lot_code for mv in moves]
    assert lots[0] == 'LOT1'
    assert moves[0].qty == Decimal('5')
    assert moves[1].qty == Decimal('3')
    # WIP total qty 8
    wip_q = StockQuant.objects.get(item=item, location=wip_loc)
    assert wip_q.qty == Decimal('8')

