from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ("prodaja", "0002_invoice_models"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="number",
            field=models.CharField(max_length=30, blank=True),
        ),
        migrations.AddConstraint(
            model_name="invoice",
            constraint=models.UniqueConstraint(
                fields=["tenant", "number"],
                name="uniq_invoice_tenant_number_nonblank",
                condition=~Q(number=""),
            ),
        ),
    ]
