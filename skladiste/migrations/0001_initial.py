"""Minimal initial stub migration for skladiste app.

All original legacy structures removed. Only bare placeholder models are
created to satisfy foreign key dependencies in historical migrations of
other apps. Future required fields should be added via new migrations,
not by editing this file.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Artikl",
            fields=[("id", models.AutoField(primary_key=True, serialize=False))],
            options={
                "verbose_name": "Artikl (stub)",
                "verbose_name_plural": "Artikli (stub)",
            },
        ),
        migrations.CreateModel(
            name="Zona",
            fields=[("id", models.AutoField(primary_key=True, serialize=False))],
            options={
                "verbose_name": "Zona (stub)",
                "verbose_name_plural": "Zone (stub)",
            },
        ),
        migrations.CreateModel(
            name="Materijal",
            fields=[("id", models.AutoField(primary_key=True, serialize=False))],
            options={
                "verbose_name": "Materijal (stub)",
                "verbose_name_plural": "Materijali (stub)",
            },
        ),
        migrations.CreateModel(
            name="Primka",
            fields=[("id", models.AutoField(primary_key=True, serialize=False))],
            options={
                "verbose_name": "Primka (stub)",
                "verbose_name_plural": "Primke (stub)",
            },
        ),
    ]
