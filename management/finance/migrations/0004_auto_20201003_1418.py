# Generated by Django 3.0 on 2020-10-03 14:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_auto_20201003_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banktransaction',
            name='shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='for_shop', to='finance.Shop'),
        ),
    ]