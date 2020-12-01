from datetime import datetime, date

from django.contrib import admin
from django.template.response import TemplateResponse
from django.db.models import Sum

from .models import *
from finance.models import Counterparty, Cost

# Register your models here.

class SalaryAdmin(admin.ModelAdmin):
    fields = ('name', 'salary', ('hire_date', 'fire_date'))
    list_display = ('name', 'salary', 'fire_date')
    list_filter = ('fire_date',)
    list_editable = ('salary', 'fire_date')
    actions = ['calculate_salary']
    ordering = ('name',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "name":
            employee = Salary.objects.all()
            kwargs["queryset"] = Counterparty.objects.filter(
                                                group__name="Employee")\
                                                     .exclude(
                                                wage_rate__in=employee)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def calculate_salary(self, request, queryset):
        opts = self.model._meta
        app_label = opts.app_label
        month_list = ['January', 'February', 'March', 'April',
                    'May', 'June', 'July','August', 'September',
                    'October', 'November', 'December']
        year = datetime.today().year

        if request.POST.get('month') and request.POST.get('half_month'):
            work_month = month_list.index(request.POST.get('month')) + 1
            work_year = int(request.POST.get('year')) 
            half_month = request.POST.get('half_month')
            if half_month == "half1":
                salary_date = date(work_year, work_month, 16)
            else:
                month_salary = (work_month + 1) % 12
                if month_salary == 1:
                    year_salary = work_year + 1
                else:
                    year_salary = work_year
                salary_date = date(year_salary, month_salary, 1)
            cost_type = Cost.objects.get(name="Salary")
            for obj in queryset:
                if half_month == "half1":
                    work_hours = obj.work_day.filter(date__month=work_month,
                                                     date__year=work_year,
                                                     date__day__lte=15)\
                                             .aggregate(Sum('hours'))
                else:
                    work_hours = obj.work_day.filter(date__month=work_month,
                                                     date__year=work_year,
                                                     date__day__gt=15)\
                                             .aggregate(Sum('hours'))
                if not work_hours['hours__sum']:
                    work_hours['hours__sum'] = 0
                amount = work_hours['hours__sum'] * float(obj.salary)
                accrued_salary = Payroll.objects.create(date=salary_date,
                                                        name=obj.name,
                                                        amount=amount,
                                                        payment=False,
                                                        salary_type=cost_type)

            return None

        context = {
            **self.admin_site.each_context(request),
            'queryset': queryset,
            'opts': opts,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
            'media': self.media,
            'months': month_list,
            'year': year,
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(request,
            "admin/calculate_salary.html", context)
    calculate_salary.short_description = "Calculate salary to the marked employees"


class PayrollAdmin(admin.ModelAdmin):
    fields = ('date', 'name', 'amount', 'payment', 'salary_type')
    list_display = ('date', 'name', 'amount')
    list_filter = ('date', 'payment', 'salary_type')
    list_editable = ('amount',)


admin.site.register(Salary, SalaryAdmin)
admin.site.register(TimeSheet)
admin.site.register(Payroll, PayrollAdmin)
