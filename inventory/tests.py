import pytest
from decimal import Decimal
from tenants.models import Tenant
from inventory.models import UoM, Item, Warehouse, Location, receive_inventory, StockQuant

pytestmark = pytest.mark.django_db


def test_receive_wac_basic():
    tenant = Tenant.objects.create(name='T1')
    m = UoM.objects.create(code='M', name='Metar')
    item = Item.objects.create(sku='PROFIL-UNP80', name='U profil', uom_base=m, item_type=Item.MATERIAL, has_lots=False)
    wh = Warehouse.objects.create(code='MAIN', name='Glavno')
    loc = Location.objects.create(warehouse=wh, code='A1', type=Location.BIN)
    # First receipt 10 @3
    move1, quant1 = receive_inventory(tenant=tenant, item=item, warehouse=wh, location=loc, qty=Decimal('10'), price_per_uom=Decimal('3'), ref='PO1')
    assert quant1.qty == Decimal('10')
    assert quant1.cost_per_uom == Decimal('3')
    # Second receipt 10 @4 -> avg 3.5
    move2, quant2 = receive_inventory(tenant=tenant, item=item, warehouse=wh, location=loc, qty=Decimal('10'), price_per_uom=Decimal('4'), ref='PO2')
    assert quant2.qty == Decimal('20')
    assert quant2.cost_per_uom.quantize(Decimal('0.000001')) == Decimal('3.500000')

