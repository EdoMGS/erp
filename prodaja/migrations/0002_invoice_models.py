# Generated manually for MVP invoice models
from decimal import Decimal

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


def create_initial_sequences(apps, schema_editor):
    # No seed data needed
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('prodaja', '0001_initial'),
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvoiceSequence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('last_number', models.IntegerField(default=0)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.tenant')),
            ],
            options={'unique_together': {('tenant', 'year')}},
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(blank=True, max_length=30, unique=True)),
                ('issue_date', models.DateField(default=django.utils.timezone.now)),
                ('client_name', models.CharField(max_length=255)),
                (
                    'status',
                    models.CharField(
                        choices=[('draft', 'Draft'), ('posted', 'Posted'), ('cancelled', 'Cancelled')],
                        default='draft',
                        max_length=20,
                    ),
                ),
                ('currency', models.CharField(default='EUR', max_length=3)),
                ('note', models.TextField(blank=True, default='')),
                ('total_base', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=14)),
                ('total_tax', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=14)),
                ('total_amount', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=14)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.tenant')),
            ],
            options={'ordering': ['-issue_date', '-id']},
        ),
        migrations.CreateModel(
            name='InvoiceLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('qty', models.DecimalField(decimal_places=2, default=Decimal('1'), max_digits=12)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('tax_rate', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=5)),
                ('base_amount', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=14)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=14)),
                ('total_amount', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=14)),
                (
                    'invoice',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='prodaja.invoice'
                    ),
                ),
            ],
        ),
        migrations.RunPython(create_initial_sequences, reverse_code=migrations.RunPython.noop),
    ]
