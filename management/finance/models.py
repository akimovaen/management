from django.db import models

# Create your models here.

class Trademark(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"


class Shop(models.Model):
    name = models.CharField(max_length=30)
    trademark = models.ForeignKey(Trademark, on_delete=models.CASCADE,
                                  related_name="shop_td")
    adress = models.CharField(max_length=128, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class CounterpartyGroup(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"


class Counterparty(models.Model):
    name = models.CharField(max_length=128)
    group = models.ForeignKey(CounterpartyGroup, on_delete=models.CASCADE,
                              related_name="group_member")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        ordering = ['name']


class CostType(models.Model):
    name = models.CharField(max_length=50)
    counterparty = models.ForeignKey(CounterpartyGroup,
                                     on_delete=models.CASCADE,
                                     related_name="cost_type",
                                     null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class Cost(models.Model):
    name = models.CharField(max_length=128)
    cost_type = models.ForeignKey(CostType, on_delete=models.CASCADE,
                                  related_name="cost")
    active = models.BooleanField(default=True)
    income = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"


class ShopCash(models.Model):
    date = models.DateField('day')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="cash_shop")
    cost = models.ForeignKey(Cost, on_delete=models.CASCADE, related_name="cash_cost")
    counterparty = models.ForeignKey(Counterparty,
                                     on_delete=models.CASCADE,
                                     related_name="cash_counterparty",
                                     null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    comment = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.shop}: {self.date}-{self.cost}"


class BankAccount(models.Model):
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


class BankTransaction(models.Model):
    date = models.DateField('day')
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE,
                                related_name="transaction", null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE,
                             related_name="bank_shop", null=True, blank=True)
    cost = models.ForeignKey(Cost, on_delete=models.CASCADE,
                             related_name="bank_cost")
    counterparty = models.ForeignKey(Counterparty,
                                     on_delete=models.CASCADE,
                                     related_name="bank_counterparty",
                                     null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.CharField(max_length=50, blank=True, null=True)
