# Generated by Django 3.0 on 2020-10-03 13:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_remove_trademark_comments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banktransaction',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='account', to='finance.BankAccount'),
        ),
    ]
