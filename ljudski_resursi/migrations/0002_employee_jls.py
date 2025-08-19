from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ljudski_resursi", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="oib",
            field=models.CharField(blank=True, default="", help_text="OIB zaposlenika", max_length=11),
        ),
        migrations.AddField(
            model_name="employee",
            name="jls_code",
            field=models.CharField(
                blank=True, default="", help_text="JLS prebivališta (npr. RIJEKA, BAKAR, ZAGREB)", max_length=20
            ),
        ),
    ]
