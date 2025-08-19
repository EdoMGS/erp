import pytest
from decimal import Decimal
from tenants.models import Tenant
from inventory.models import (
    UoM, Item, Warehouse, Location, receive_inventory, WorkOrder,
    execute_cut_plan, mix_paint, adjust_inventory
)

pytestmark = pytest.mark.django_db


def base_setup():
    tenant = Tenant.objects.create(name='TINV')
    m = UoM.objects.create(code='L', name='Litra')
    mb = UoM.objects.create(code='M', name='Metar')
    wh = Warehouse.objects.create(code='MAIN', name='Main')
    bin_loc = Location.objects.create(warehouse=wh, code='BIN', type=Location.BIN)
    wip_loc = Location.objects.create(warehouse=wh, code='WIP', type=Location.WIP)
    scrap_loc = Location.objects.create(warehouse=wh, code='SCR', type=Location.SCRAP)
    base = Item.objects.create(sku='BOJA-A', name='Boja baza', uom_base=m, item_type=Item.PAINT, has_lots=True, is_paint_component=True)
    hardener = Item.objects.create(sku='HARD-B', name='Hardener', uom_base=m, item_type=Item.PAINT, has_lots=True, is_paint_component=True)
    thinner = Item.objects.create(sku='THIN-C', name='Thinner', uom_base=m, item_type=Item.CONSUMABLE, has_lots=True, is_paint_component=True)
    profile = Item.objects.create(sku='PROFIL-UNP80', name='Profil', uom_base=mb, item_type=Item.MATERIAL, has_lots=False, track_length=True)
    return tenant, wh, bin_loc, wip_loc, scrap_loc, base, hardener, thinner, profile


def test_paint_mix_and_adjust():
    tenant, wh, bin_loc, wip_loc, scrap_loc, base, hardener, thinner, profile = base_setup()
    receive_inventory(tenant=tenant, item=base, warehouse=wh, location=bin_loc, qty=Decimal('50'), price_per_uom=Decimal('10'), ref='RCV1', lot_code='L1')
    receive_inventory(tenant=tenant, item=hardener, warehouse=wh, location=bin_loc, qty=Decimal('20'), price_per_uom=Decimal('20'), ref='RCV2', lot_code='L2')
    receive_inventory(tenant=tenant, item=thinner, warehouse=wh, location=bin_loc, qty=Decimal('30'), price_per_uom=Decimal('5'), ref='RCV3', lot_code='L3')
    wo = WorkOrder.objects.create(code='WO-P1')
    mix = mix_paint(
        tenant=tenant,
        work_order=wo,
        base_item=base,
        qty_L=Decimal('10'),
        hardener=hardener,
        hardener_pct=Decimal('20'),
        thinner=thinner,
        thinner_pct=Decimal('10'),
        loss_pct=Decimal('5'),
        warehouse=wh,
        bin_loc=bin_loc,
        wip_loc=wip_loc,
        ref='MIX1'
    )
    assert mix.total_mix_qty > 0
    adjust_inventory(tenant=tenant, item=base, warehouse=wh, location=bin_loc, new_qty=Decimal('35'), ref='ADJ1')


def test_cut_plan_basic():
    tenant, wh, bin_loc, wip_loc, scrap_loc, base, hardener, thinner, profile = base_setup()
    receive_inventory(tenant=tenant, item=profile, warehouse=wh, location=bin_loc, qty=Decimal('12'), price_per_uom=Decimal('3'), ref='RCVP')
    wo = WorkOrder.objects.create(code='WO-C1')
    cp = execute_cut_plan(tenant=tenant, work_order=wo, item=profile, warehouse=wh, src=bin_loc, wip=wip_loc, plan_ref='CP1', cuts=[Decimal('2.4'), Decimal('2.4'), Decimal('1.0')], bar_length=Decimal('6.0'))
    assert cp.offcuts == ['0.2']
