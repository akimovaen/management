# Generated by Django 3.0 on 2020-10-28 12:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_auto_20201003_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banktransaction',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction', to='finance.BankAccount'),
        ),
        migrations.AlterField(
            model_name='banktransaction',
            name='shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bank_shop', to='finance.Shop'),
        ),
        migrations.AlterField(
            model_name='cost',
            name='cost_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cost', to='finance.CostType'),
        ),
        migrations.AlterField(
            model_name='costtype',
            name='counterparty',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cost_type', to='finance.CounterpartyGroup'),
        ),
        migrations.AlterField(
            model_name='counterparty',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_member', to='finance.CounterpartyGroup'),
        ),
        migrations.AlterField(
            model_name='shop',
            name='trademark',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shop_td', to='finance.Trademark'),
        ),
        migrations.AlterField(
            model_name='shopcash',
            name='cost',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cash_cost', to='finance.Cost'),
        ),
        migrations.AlterField(
            model_name='shopcash',
            name='counterparty',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cash_counterparty', to='finance.Counterparty'),
        ),
        migrations.AlterField(
            model_name='shopcash',
            name='shop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cash_shop', to='finance.Shop'),
        ),
    ]