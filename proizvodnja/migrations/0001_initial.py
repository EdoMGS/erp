from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="RadniNalog", fields=[("id", models.AutoField(primary_key=True, serialize=False))]
        ),
        migrations.CreateModel(
            name="Projekt", fields=[("id", models.AutoField(primary_key=True, serialize=False))]
        ),
        migrations.CreateModel(
            name="TipVozila", fields=[("id", models.AutoField(primary_key=True, serialize=False))]
        ),
        migrations.CreateModel(
            name="TipProjekta", fields=[("id", models.AutoField(primary_key=True, serialize=False))]
        ),
        migrations.CreateModel(
            name="ProizvodniResurs",
            fields=[("id", models.AutoField(primary_key=True, serialize=False))],
        ),
        migrations.CreateModel(
            name="Grupaposlova",
            fields=[("id", models.AutoField(primary_key=True, serialize=False))],
        ),
        migrations.CreateModel(
            name="TemplateRadniNalog",
            fields=[("id", models.AutoField(primary_key=True, serialize=False))],
        ),
        migrations.CreateModel(
            name="Angazman", fields=[("id", models.AutoField(primary_key=True, serialize=False))]
        ),
    ]
