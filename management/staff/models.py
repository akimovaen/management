from django.db import models
from finance.models import Counterparty, Shop, Cost

# Create your models here.

class Salary(models.Model):
    name = models.OneToOneField(Counterparty,
                             on_delete=models.CASCADE,
                             related_name="wage_rate",)
    salary = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    hire_date = models.DateField('hire date')
    fire_date = models.DateField('fire date', blank=True, null=True)
       
    def __str__(self):
        return f"{self.name}"


class TimeSheet(models.Model):
    date = models.DateField('day')
    name = models.ForeignKey(Salary,
                             on_delete=models.CASCADE,
                             related_name="work_day",)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="timesheet")
    hours = models.FloatField('hours worked')

    def __str__(self):
        return f"{self.shop}: {self.date}-{self.name}"


class Payroll(models.Model):
    date = models.DateField('day')
    name = models.ForeignKey(Counterparty,
                             on_delete=models.CASCADE,
                             related_name="salary",)
    amount = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    payment = models.BooleanField(default=True)
    salary_type = models.ForeignKey(Cost, on_delete=models.CASCADE,
                                    related_name="salary_payment")
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE,
                             related_name="payroll", blank=True, null=True)

    def __str__(self):
        return f"{self.name}: {self.date}-{self.salary_type}"
