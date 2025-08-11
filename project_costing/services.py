from project_costing.models import CostLine


def import_invoice_to_costline(invoice, project):
    """
    InvoiceIn → CostLine(type='MAT')
    """
    for line in invoice.lines.all():
        CostLine.objects.create(
            project=project,
            type="MAT",
            description=line.description,
            amount=line.line_total,
        )


def import_assetusage_to_costline(asset_usage, project):
    """
    AssetUsage → CostLine(type='ENE')
    """
    CostLine.objects.create(
        project=project,
        type="ENE",
        description=str(asset_usage),
        amount=getattr(asset_usage, "amount", 0),
    )


def import_reklamacija_to_costline(reklamacija, project):
    """
    Reklamacija → CostLine(type='OTH')
    """
    CostLine.objects.create(
        project=project,
        type="OTH",
        description=str(reklamacija),
        amount=getattr(reklamacija, "amount", 0),
    )
