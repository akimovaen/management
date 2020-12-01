import calendar

from datetime import date, datetime

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic import TemplateView, RedirectView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
from django.db.models import Sum, Q

from .models import *
from .forms import *
from finance.models import Counterparty, Shop, Cost
from finance import util

# Create your views here.

# This view render a table with accrued and paid salary for each person this month (if month_delta = 0).
# Month_delta shows the deviation from the current month.
class StaffListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    template_name = 'staff/staff_list.html'
    model = Payroll

    def get(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
    
            return super().get(request, *args, **kwargs)
        
        else:
            
            return HttpResponseRedirect(reverse('finance:no-access'))

    def aggregate_data(self):
        prev_month = util.plus_minus_month(year_month=self.month, plus=False)
        next_month = util.plus_minus_month(year_month=self.month, plus=True)
        employee = Counterparty.objects.filter(group__name="Employee")
        cost_prepayment = Cost.objects.get(name="Prepayment")
        cost_bonus = Cost.objects.get(name="Bonus")
        cost_salary = Cost.objects.get(name="Salary")
        salary_payment = [{'name': 'prev_accrued_salary','cost': cost_salary,
                        'month':self.month['month'],'year':self.month['year'],
                        'last_date': 15, 'payment': False},
                        {'name': 'prev_prepayment', 'cost': cost_prepayment,
                        'month':prev_month['month'],'year':prev_month['year'],
                        'first_date': 16, 'payment': True},
                        {'name': 'prev_paid_salary', 'cost': cost_salary,
                        'month':self.month['month'],'year':self.month['year'],
                        'last_date': 15, 'payment': True},
                        {'name': 'first_prepayment', 'cost': cost_prepayment,
                        'month':self.month['month'],'year':self.month['year'],
                        'last_date': 15, 'payment': True},
                        {'name': 'first_bonus', 'cost': cost_bonus, 
                        'month':self.month['month'],'year':self.month['year'],
                        'last_date': 15, 'payment': True},
                        {'name': 'first_accrued_salary', 'cost': cost_salary,
                        'month':self.month['month'],'year':self.month['year'],
                        'first_date': 16, 'payment': False},
                        {'name': 'first_paid_salary', 'cost': cost_salary,
                        'month':self.month['month'],'year':self.month['year'],
                        'first_date': 16, 'payment': True},
                        {'name': 'second_prepayment', 'cost': cost_prepayment,
                        'month':self.month['month'],'year':self.month['year'],
                        'first_date': 16, 'payment': True},
                        {'name': 'second_bonus', 'cost': cost_bonus,
                        'month':self.month['month'],'year':self.month['year'],
                        'first_date': 16, 'payment': True},
                        {'name': 'second_accrued_salary', 'cost': cost_salary,
                        'month':next_month['month'],'year':next_month['year'],
                        'last_date': 15, 'payment': False}]
        for payment in salary_payment:
            if 'first_date' in payment:
                totals = Sum('salary__amount',
                        filter=Q(salary__date__month=payment['month'],
                                 salary__date__year=payment['year'],
                                 salary__date__day__gte=payment['first_date'],
                                 salary__payment=payment['payment'],
                                 salary__salary_type=payment['cost']))
            else:
                totals = Sum('salary__amount',
                        filter=Q(salary__date__month=payment['month'],
                                 salary__date__year=payment['year'],
                                 salary__date__day__lte=payment['last_date'],
                                 salary__payment=payment['payment'],
                                 salary__salary_type=payment['cost']))
            payment['totals'] = employee.annotate(totals=totals)
        for person in employee:
            person.totals = {}
            for payment in salary_payment:
                payment_data = payment['totals'].get(id=person.id)
                if payment['name'] == 'prev_accrued_salary':
                    prev_accrued_salary = payment_data.totals
                elif payment['name'] == 'prev_prepayment':
                    prev_prepayment = payment_data.totals
                elif payment['name'] == 'prev_paid_salary':
                    prev_paid_salary = payment_data.totals
                else:
                    person.totals[payment['name']] = payment_data.totals
            if not prev_accrued_salary:
                prev_accrued_salary = 0
            if not prev_prepayment:
                prev_prepayment = 0
            if not prev_paid_salary:
                prev_paid_salary = 0
            person.totals['prev_salary'] = prev_accrued_salary\
                                         - prev_prepayment\
                                         - prev_paid_salary
        
        return employee

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shops'] = Shop.objects.all()
        self.month = util.view_month(self.kwargs['month_delta'])
        context['staff'] = self.aggregate_data()
        context['month_delta'] = self.kwargs['month_delta']
        context['month_name'] = util.month_name(self.month['month'])
        
        return context


# This view render a table with shop's timesheet this month (if month_delta = 0).
# Month_delta shows the deviation from the current month.
class ShopTimesheetView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    template_name='staff/shop_month.html'
    model = TimeSheet

    def get(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
    
            return super().get(request, *args, **kwargs)
        
        else:
            
            return HttpResponseRedirect(reverse('finance:no-access'))

    def aggregate_data(self):
        staff = Salary.objects.filter(fire_date=None)
        by_days = {}
        for day in range(self.days_in_month[1]):
            by_days[day] = staff.annotate(day_hours=Sum("work_day__hours",
                    filter=Q(work_day__date__year=self.month['year'],
                             work_day__date__month=self.month['month'],
                             work_day__date__day=day+1,
                             work_day__shop__id=self.kwargs['pk'])))
        for person in staff:
            person.days = {}
            for day in range(self.days_in_month[1]):
                day_data = by_days[day].get(id=person.id)
                person.days[day+1] = day_data.day_hours

        return staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shops'] = Shop.objects.all()
        context['shop'] = get_object_or_404(Shop, id=self.kwargs['pk'])
        self.month = util.view_month(self.kwargs['month_delta'])
        self.days_in_month = calendar.monthrange(self.month['year'],
                                                 self.month['month'])
        context['weekdays'] = util.weekdays_in_month(self.days_in_month[0],
                                                     self.days_in_month[1])
        context['month_name'] = util.month_name(self.month['month'])
        context['month_delta'] = self.kwargs['month_delta']
        context['month'] = self.month
        context['data'] = self.aggregate_data()

        return context


# This view renders a template with form to chose date of the shop's timesheet.
class SelectTimesheetView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name='staff/timesheet_select.html'

    def get(self, request, *args, **kwargs):
        self.shop = get_object_or_404(Shop, id=self.kwargs['pk'])
        if self.request.user.first_name == self.shop.name\
                                        or self.request.user.is_superuser:
    
            return super().get(request, *args, **kwargs)
        
        else:
            
            return HttpResponseRedirect(reverse('finance:no-access'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shops'] = Shop.objects.all()
        context['shop'] = self.shop
        
        return context

    def post(self, request, **kwargs):
        report_date = request.POST.get('day')
        pk = self.kwargs['pk']
        try:
            valid_date = datetime.strptime(report_date, "%Y-%m-%d")
            year = valid_date.year
            month = valid_date.month
            day = valid_date.day
           
            return HttpResponseRedirect(reverse('staff:timesheet-view',
                                                args=(pk, year, month, day,)))
        
        except ValueError:

            return self.render_to_response(self.get_context_data(**kwargs))


# This view renders a form to enter the work hours of shop's staff a day and
# a table with saved ones.
class TimesheetCreateView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    template_name='staff/timesheet_form.html'
    form_class = TimesheetForm

    def get_initial(self):
        self.day = date(self.kwargs['year'], self.kwargs['month'], self.kwargs['day'])
        self.shop = get_object_or_404(Shop, id=self.kwargs['pk'])
        self.initial = {'shop': self.shop, 'date': self.day}
        self.success_url = reverse('staff:timesheet-view', args=(self.kwargs['pk'],
                                                                self.kwargs['year'],
                                                                self.kwargs['month'],
                                                                self.kwargs['day'],))

        return self.initial.copy()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shops'] = Shop.objects.all()
        context['shop'] = self.shop
        context['day'] = self.day
        context['data'] = TimeSheet.objects.filter(shop=self.shop,
                                                   date=self.day)\
                                           .order_by('name__name')
        
        return context

    def get(self, request, *args, **kwargs):
        self.shop = get_object_or_404(Shop, id=self.kwargs['pk'])
        if self.request.user.first_name == self.shop.name\
                                        or self.request.user.is_superuser:
            try:

                return super().get(request, *args, **kwargs)

            except ValueError:

                return HttpResponseRedirect(reverse('staff:select-timesheet',
                                                    args=(self.kwargs['pk'],)))
        
        else:
            
            return HttpResponseRedirect(reverse('finance:no-access'))


# This view renders a form to edit the shop's timesheet.
class TimesheetEditView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    template_name='staff/edit_form.html'
    form_class = TimesheetForm
    model = TimeSheet
    # fields = ['name', 'hours', 'shop', 'date']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        year = self.object.date.year
        month = self.object.date.month
        day = self.object.date.day
        self.success_url = reverse('staff:timesheet-view',
                           args=(self.object.shop.id, year, month, day,))

        return super().post(request, *args, **kwargs)


# This view renders a form to delete the items of shop's timesheet.
class TimesheetDeleteView(LoginRequiredMixin, DeleteView):
    login_url = '/login/'
    template_name='staff/delete_form.html'
    model = TimeSheet

    def get_object(self, queryset=None):
        self.object = super().get_object()
        self.success_url = reverse('staff:timesheet-view',
                                    args=(self.object.shop.id,
                                          self.object.date.year,
                                          self.object.date.month,
                                          self.object.date.day,))
        return self.object   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = self.object.shop.id
        year = self.object.date.year
        month = self.object.date.month
        day = self.object.date.day
        context['success'] = f"/staff/{shop}/timesheet/{year}/{month}/{day}/"

        return context
