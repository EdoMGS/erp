"""Skeleton migration to replace previously empty file.

Acts as a no-op placeholder after lost original operations.
Further intended constraints for journal items should be recreated in a new migration.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("financije", "0008_journalitem_constraints_indexes"),
    ]

    operations = []
