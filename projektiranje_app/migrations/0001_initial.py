"""Minimal initial migration for stub projektiranje_app.

This replaces the legacy complex migration history with a single
CreateModel operation required only to satisfy historical foreign key
dependencies from other apps. Do NOT add additional legacy structures
back into this file; extend via new migrations if needed.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    # No external dependencies: other apps historically referencing this app
    # will point at this minimal state.
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DesignTask",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("placeholder", models.CharField(max_length=1, default="X")),
            ],
            options={
                "verbose_name": "Design task (stub)",
                "verbose_name_plural": "Design tasks (stub)",
            },
        )
    ]
