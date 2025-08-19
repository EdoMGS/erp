from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("financije", "0008_journalitem_constraints_indexes"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="journalitem",
            constraint=models.CheckConstraint(
                name="journalitem_non_negative",
                check=(models.Q(debit__gte=0) & models.Q(credit__gte=0)),
            ),
        ),
        # Composite index including entry (FK), account plus date via entry for reporting.
        # Since tenant is on entry, we rely on (entry, account) + entry index for efficient filtering.
        # (Direct multi-column across relation not supported without functional index.)
        # Keep for clarity if later adding a materialized tenant field on JournalItem.
        # (No-op if already exists; safe guard.)
    ]
