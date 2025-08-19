from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("financije", "0007_postedjournalref"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="journalitem",
            constraint=models.CheckConstraint(
                name="journalitem_debit_xor_credit",
                check=(models.Q(debit__gt=0, credit=0) | models.Q(credit__gt=0, debit=0) | models.Q(debit=0, credit=0)),
            ),
        ),
        migrations.AddIndex(
            model_name="journalitem",
            index=models.Index(fields=["entry", "account"], name="ji_entry_acct_idx"),
        ),
        migrations.AddIndex(
            model_name="journalitem",
            index=models.Index(fields=["account"], name="ji_acct_idx"),
        ),
        migrations.AddIndex(
            model_name="journalitem",
            index=models.Index(fields=["entry"], name="ji_entry_idx"),
        ),
    ]
