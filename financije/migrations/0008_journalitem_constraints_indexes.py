"""Skeleton migration to replace previously empty file.

Original content lost; recreated as no-op to satisfy Django migration loader.
If constraints/indexes were intended, reintroduce them in a new migration.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("financije", "0007_alter_budget_options_alter_invoice_options_and_more"),
    ]

    operations = []
