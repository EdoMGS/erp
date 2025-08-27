from django.db import migrations


class Migration(migrations.Migration):

    # This merge resolves two branches that diverged at 0005_apiidempotency:
    #  - 0006_blob -> 0007_blob_retention
    #  - 0006_rename_api_idem_tpmk_idx_common_apii_tenant__998aab_idx_and_more
    # No schema changes here; it only unifies the graph.

    dependencies = [
        ("common", "0007_blob_retention"),
        (
            "common",
            "0006_rename_api_idem_tpmk_idx_common_apii_tenant__998aab_idx_and_more",
        ),
    ]

    operations = []
