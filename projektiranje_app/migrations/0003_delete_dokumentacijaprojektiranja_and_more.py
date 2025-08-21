from django.db import migrations


class Migration(migrations.Migration):
    # Legacy migration collapsed to no-op for stubbed app; remove dependency on proizvodnja.
    dependencies = [
        ("projektiranje_app", "0002_caddocument_designrevision_designsegment_dynamicplan_and_more"),
    ]
    operations = []
