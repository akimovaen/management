from django.contrib import admin

from .models import *

# Register your models here.

class CounterpartyAdmin(admin.ModelAdmin):
    list_filter = ('group',)


class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'cost', 'amount', 'shop')

admin.site.register(Trademark)
admin.site.register(Shop)
admin.site.register(CounterpartyGroup)
admin.site.register(Counterparty, CounterpartyAdmin)
admin.site.register(CostType)
admin.site.register(Cost)
admin.site.register(ShopCash)
admin.site.register(BankAccount)
admin.site.register(BankTransaction, BankTransactionAdmin)
