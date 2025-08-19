from decimal import Decimal

import pytest

from financije.models.accounting import Account, JournalItem
from inventory.models import (
    Item,
    Location,
    UoM,
    Warehouse,
    WorkOrder,
    finish_work_order,
    issue_to_wip,
    receive_inventory,
    return_from_wip,
    scrap_from_wip,
)
from tenants.models import Tenant

pytestmark = pytest.mark.django_db


def sum_account(number: str):
    acct = Account.objects.get(number=number)
    agg = acct.journalitem_set.aggregate_django = acct.journalitem_set.aggregate  # type: ignore[attr-defined]
    debit = acct.journalitem_set.aggregate(debit_sum=pytest.django.compat.dj_models.Sum("debit"))[
        'debit_sum'
    ] or Decimal('0')
    credit = acct.journalitem_set.aggregate(credit_sum=pytest.django.compat.dj_models.Sum("credit"))[
        'credit_sum'
    ] or Decimal('0')
    return debit, credit, debit - credit


def test_issue_return_scrap_gl_amounts():
    tenant = Tenant.objects.create(name='GL1')
    m = UoM.objects.create(code='M', name='Metar')
    item = Item.objects.create(sku='PROFILE', name='Profil', uom_base=m, item_type=Item.MATERIAL, has_lots=False)
    wh = Warehouse.objects.create(code='W', name='Main')
    bin_loc = Location.objects.create(warehouse=wh, code='BIN', type=Location.BIN)
    wip_loc = Location.objects.create(warehouse=wh, code='WIP', type=Location.WIP)
    scrap_loc = Location.objects.create(warehouse=wh, code='SCR', type=Location.SCRAP)
    receive_inventory(
        tenant=tenant,
        item=item,
        warehouse=wh,
        location=bin_loc,
        qty=Decimal('10'),
        price_per_uom=Decimal('3'),
        ref='PO1',
    )  # 30
    issue_to_wip(tenant=tenant, item=item, warehouse=wh, src=bin_loc, wip=wip_loc, qty=Decimal('6'), ref='ISS1')  # 18
    return_from_wip(tenant=tenant, item=item, warehouse=wh, wip=wip_loc, dst=bin_loc, qty=Decimal('2'), ref='RET1')  # 6
    scrap_from_wip(
        tenant=tenant, item=item, warehouse=wh, wip=wip_loc, scrap_loc=scrap_loc, qty=Decimal('1'), ref='SCR1'
    )  # 3

    # Aggregate journal items
    from django.db.models import Sum

    def acct_sums(num):
        ji = JournalItem.objects.filter(account__number=num)
        deb = ji.aggregate(Sum('debit'))['debit__sum'] or Decimal('0')
        cred = ji.aggregate(Sum('credit'))['credit__sum'] or Decimal('0')
        return deb, cred, deb - cred

    inv = acct_sums('140')  # Expect DR 36 CR 18 => net 18
    wip = acct_sums('150')  # DR 18 CR 9 => net 9
    scrap = acct_sums('699')  # DR 3
    ap = acct_sums('220')  # CR 30

    assert inv == (Decimal('36.00'), Decimal('18.00'), Decimal('18.00'))
    assert wip == (Decimal('18.00'), Decimal('9.00'), Decimal('9.00'))
    assert scrap[0] == Decimal('3.00') and scrap[1] == Decimal('0.00')
    assert ap[1] == Decimal('30.00')
    # Accounting equation check: total DR == total CR
    total_dr = sum(x[0] for x in [inv, wip, scrap])
    total_cr = inv[1] + wip[1] + ap[1]
    assert total_dr == total_cr


def test_finish_work_order_gl_amounts():
    tenant = Tenant.objects.create(name='GL2')
    m = UoM.objects.create(code='M', name='Metar')
    item = Item.objects.create(sku='PROFILE2', name='Profil2', uom_base=m, item_type=Item.MATERIAL, has_lots=False)
    wh = Warehouse.objects.create(code='W2', name='Main2')
    bin_loc = Location.objects.create(warehouse=wh, code='BIN', type=Location.BIN)
    wip_loc = Location.objects.create(warehouse=wh, code='WIP', type=Location.WIP)
    scrap_loc = Location.objects.create(warehouse=wh, code='SCR', type=Location.SCRAP)
    wo = WorkOrder.objects.create(code='WO-GL2')
    receive_inventory(
        tenant=tenant,
        item=item,
        warehouse=wh,
        location=bin_loc,
        qty=Decimal('10'),
        price_per_uom=Decimal('3'),
        ref='PO1',
    )  # 30
    issue_to_wip(
        tenant=tenant, item=item, warehouse=wh, src=bin_loc, wip=wip_loc, qty=Decimal('6'), ref='ISS1', work_order=wo
    )  # 18 into WIP
    scrap_from_wip(
        tenant=tenant,
        item=item,
        warehouse=wh,
        wip=wip_loc,
        scrap_loc=scrap_loc,
        qty=Decimal('1'),
        ref='SCR1',
        work_order=wo,
    )  # 3 scrap
    finish_work_order(tenant=tenant, work_order=wo, ref='FIN1')  # Remaining 5*3=15 to COGS

    from django.db.models import Sum

    def acct_sums(num):
        ji = JournalItem.objects.filter(account__number=num)
        deb = ji.aggregate(Sum('debit'))['debit__sum'] or Decimal('0')
        cred = ji.aggregate(Sum('credit'))['credit__sum'] or Decimal('0')
        return deb, cred, deb - cred

    inv = acct_sums('140')  # DR 30 CR 18 => net 12 (4 units remain)
    wip = acct_sums('150')  # DR 18 CR (3+15)=18 => net 0
    scrap = acct_sums('699')  # DR 3
    cogs = acct_sums('500')  # DR 15
    ap = acct_sums('220')  # CR 30

    assert inv == (Decimal('30.00'), Decimal('18.00'), Decimal('12.00'))
    assert wip == (Decimal('18.00'), Decimal('18.00'), Decimal('0.00'))
    assert scrap[0] == Decimal('3.00') and scrap[1] == Decimal('0.00')
    assert cogs[0] == Decimal('15.00')
    assert ap[1] == Decimal('30.00')
    total_dr = sum(x[0] for x in [inv, wip, scrap, cogs])
    total_cr = inv[1] + wip[1] + ap[1]
    assert total_dr == total_cr
