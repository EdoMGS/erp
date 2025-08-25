from django.db import migrations, models
import django.utils.timezone
import datetime


def set_retained_until(apps, schema_editor):
    Blob = apps.get_model("common", "Blob")
    for blob in Blob.objects.all():
        blob.retained_until = blob.created_at + datetime.timedelta(days=365 * 11)
        blob.save(update_fields=["retained_until"])


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0006_blob"),
    ]

    operations = [
        migrations.AddField(
            model_name="blob",
            name="retained_until",
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.RunPython(set_retained_until, migrations.RunPython.noop),
    ]
