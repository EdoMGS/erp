from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tenants", "0001_initial"),
        ("proizvodnja", "0007_alter_angazman_id_alter_grupaposlova_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaintLot",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("color", models.CharField(max_length=32)),
                ("received_at", models.DateField()),
                ("remaining_qty", models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="tenants.tenant")),
            ],
        ),
        migrations.CreateModel(
            name="Reservation",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("quantity", models.DecimalField(max_digits=10, decimal_places=2)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "lot",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="inventory.paintlot"),
                ),
                (
                    "tenant",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="tenants.tenant"),
                ),
                (
                    "work_order",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="proizvodnja.radninalog"),
                ),
            ],
        ),
    ]
