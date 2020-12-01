# Generated by Django 3.0 on 2020-10-28 12:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0005_auto_20201028_1201'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payroll',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salary', to='finance.Counterparty'),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='salary_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salary_payment', to='finance.Cost'),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payroll', to='finance.Shop'),
        ),
        migrations.AlterField(
            model_name='salary',
            name='name',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='wage_rate', to='finance.Counterparty'),
        ),
        migrations.AlterField(
            model_name='timesheet',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_day', to='staff.Salary'),
        ),
        migrations.AlterField(
            model_name='timesheet',
            name='shop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timesheet', to='finance.Shop'),
        ),
    ]
