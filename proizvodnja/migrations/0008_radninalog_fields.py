from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("tenants", "0001_initial"),
        ("proizvodnja", "0007_alter_angazman_id_alter_grupaposlova_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="radninalog",
            name="tenant",
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to="tenants.tenant"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="radninalog",
            name="quote_id",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="radninalog",
            name="option",
            field=models.CharField(default="", max_length=16),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name="radninalog",
            unique_together={("tenant", "quote_id", "option")},
        ),
    ]
