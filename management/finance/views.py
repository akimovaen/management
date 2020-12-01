import json
import calendar

from datetime import date, timedelta, datetime

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic import TemplateView, RedirectView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.db.models import Max, Sum, Count, Q, F
from django.urls import reverse

from management.settings import BALANCE, REVENUE, BANK, SALARY
from .models import *
from staff.models import Payroll
from . import util

 

# This view render a table with revenue, expenses and profit for each shop this month (if month_delta = 0).
# Month_delta shows the deviation from the current month.
class ShopListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    template_name = 'finance/shop_list.html'
    model = Shop

    def get(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
    
            return super().get(request, *args, **kwargs)
        
        else:
            
            return HttpResponseRedirect(reverse('finance:greeting'))

    def aggregate_data(self, cost_type):
        costs = Cost.objects.filter(cost_type=cost_type)
        for cost in costs:
            cash=Sum('cash_shop__amount',
                    filter=Q(cash_shop__date__month=self.month['month'],
                            cash_shop__date__year=self.month['year'],
                            cash_shop__cost=cost))
            shops = Shop.objects.annotate(total=cash)
            bank=Sum('bank_shop__amount',
                    filter=Q(bank_shop__date__month=self.month['month'],
                            bank_shop__date__year=self.month['year'],
                            bank_shop__cost=cost))
            shops_bank = Shop.objects.annotate(bank=bank)
            for shop in shops:
                if not shop.total:
                    shop.total = 0
                bank = shops_bank.get(id=shop.id)
                if not bank.bank:
                    bank.bank = 0
                shop.total += bank.bank
            cost.shops = shops    

        return costs

    def get_context_data(self, **kwargs):
        self.month = util.view_month(self.kwargs['month_delta'])
        context = super().get_context_data(**kwargs)
        context['trademark_list'] = Trademark.objects.annotate(
                                    shops=Count('shop_td'))
        context['shops'] = Shop.objects.all()
        context['month'] = util.month_name(self.month['month'])
        context['month_delta'] = self.kwargs['month_delta']
        revenue = Cost.objects.get(id=REVENUE)
        cash=Sum('cash_shop__amount',
                 filter=Q(cash_shop__date__month=self.month['month'],
                          cash_shop__date__year=self.month['year'],
                          cash_shop__cost=revenue))
        context['revenue'] = Shop.objects.annotate(cash=cash)
        cost_types = CostType.objects.exclude(id=BALANCE).exclude(id=REVENUE)
        for cost_type in cost_types:
            cost_type.costs = self.aggregate_data(cost_type) 
        context['cost_types'] = cost_types

        return context


# This view render a table with shop's cash this month (if month_delta = 0).
# Month_delta shows the deviation from the current month.
class ShopDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    template_name='finance/shop_month.html'
    model = Shop

    def get(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
    
            return super().get(request, *args, **kwargs)
        
        else:
            
            return HttpResponseRedirect(reverse('finance:no-access'))

    def aggregate_data(self):
        types = CostType.objects.all()
        for cost_type in types:
            if cost_type.id == REVENUE:
                cost_type.name = "Cash revenue"
                total = cost_type.cost.filter(id=REVENUE)
                for cost in total:
                    cost.name = "Cash revenue"
                    cost.days = {}
                noncash = cost_type.cost.filter(id=BANK)
                for day in range(self.days_in_month[1]):
                    day_total = total.filter(
                                cash_cost__date__year=self.month['year'],
                                cash_cost__date__month=self.month['month'],
                                cash_cost__date__day=day+1,
                                cash_cost__shop__id=self.kwargs['pk'])\
                                 .aggregate(day_sum=Sum("cash_cost__amount"))
                    day_noncash = noncash.filter(
                                cash_cost__date__year=self.month['year'],
                                cash_cost__date__month=self.month['month'],
                                cash_cost__date__day=day+1,
                                cash_cost__shop__id=self.kwargs['pk'])\
                                  .aggregate(day_sum=Sum("cash_cost__amount"))
                    if not day_total['day_sum']:
                        day_total['day_sum'] = 0
                    if not day_noncash['day_sum']:
                        day_noncash['day_sum'] = 0
                    day_cash = day_total['day_sum'] - day_noncash['day_sum']
                    total[0].days[day+1] = day_cash
                cost_type.costs = total
            else:
                costs = Cost.objects.filter(cost_type=cost_type)
                by_days = {}
                for day in range(self.days_in_month[1]):
                    by_days[day] = costs.annotate(
                        day_sum=Sum("cash_cost__amount",
                        filter=Q(cash_cost__date__year=self.month['year'],
                                cash_cost__date__month=self.month['month'],
                                cash_cost__date__day=day+1,
                                cash_cost__shop__id=self.kwargs['pk'])))
                for cost in costs:
                    cost.days = {}
                    for day in range(self.days_in_month[1]):
                        day_data = by_days[day].get(id=cost.id)
                        cost.days[day+1] = day_data.day_sum
                cost_type.costs = costs
        
        return types

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.month = util.view_month(self.kwargs['month_delta'])
        self.days_in_month = calendar.monthrange(self.month['year'],
                                                 self.month['month'])
        context['shop'] = get_object_or_404(Shop, id=self.kwargs['pk'])
        context['shops'] = Shop.objects.all()
        context['data'] = self.aggregate_data()
        context['weekdays'] = util.weekdays_in_month(self.days_in_month[0],
                                                     self.days_in_month[1])
        context['month_name'] = util.month_name(self.month['month'])
        context['month_delta'] = self.kwargs['month_delta']
        context['month'] = self.month
        context['revenue'] = REVENUE
        context['balance'] = BALANCE

        return context


# This view renders a template with form to chose date of the shop's report.
class SelectReportView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name='finance/report_select.html'

    def get(self, request, *args, **kwargs):
        self.shop = get_object_or_404(Shop, id=self.kwargs['pk'])
        if self.request.user.first_name == self.shop.name\
                                        or self.request.user.is_superuser:
    
            return super().get(request, *args, **kwargs)
        
        else:
            
            return HttpResponseRedirect(reverse('finance:no-access'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['shops'] = Shop.objects.all()
        max_date = ShopCash.objects.filter(shop=context['shop'])\
                                   .aggregate(Max('date'))
        if max_date['date__max'] is None:
            context['message'] = "There are no reports."
        else:
            previous_day = max_date['date__max'] - timedelta(days=1)
            previous_day_data = ShopCash.objects.filter(shop=context['shop'],
                                                        date=previous_day)
            try:
                previous_day_data[0]
                context['last_report_date'] = previous_day
            except IndexError:
                message = f"Report from {max_date['date__max']} is not completed"
                context['message'] = message
        
        return context

    def post(self, request, **kwargs):
        report_date = request.POST.get('day')
        pk = self.kwargs['pk']
        self.shop = get_object_or_404(Shop, id=pk)
        try:
            valid_date = datetime.strptime(report_date, "%Y-%m-%d")
            year = valid_date.year
            month = valid_date.month
            day = valid_date.day
           
            return HttpResponseRedirect(reverse('finance:report-view',
                                                args=(pk, year, month, day,)))
        
        except ValueError:

            return self.render_to_response(self.get_context_data(**kwargs))


# This view renders a form to enter the items of shop's daily report and
# a table with saved items of the report.
class ReportCreateView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    template_name='finance/report_form.html'
    model = ShopCash
    fields = ['cost', 'amount', 'counterparty', 'comment', 'shop', 'date']

    def get_initial(self):
        self.day = date(self.kwargs['year'], self.kwargs['month'], self.kwargs['day'])
        shop = get_object_or_404(Shop, id=self.kwargs['pk'])
        self.initial = {'shop': shop, 'date': self.day}
        self.success_url = reverse('finance:report-view', args=(self.kwargs['pk'],
                                                                self.kwargs['year'],
                                                                self.kwargs['month'],
                                                                self.kwargs['day'],))

        return self.initial.copy()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['shops'] = Shop.objects.all()
        context['day'] = self.day
        context['cost'] = CostType.objects.all()
        context['data'] = ShopCash.objects.filter(shop=self.shop,
                                                  date=self.day)\
                                          .order_by('cost__cost_type')
        queryset_next_day = ShopCash.objects.filter(
                                    date=self.day+timedelta(days=1),
                                    shop=self.shop,
                                    cost__id=BALANCE)
        try:
            queryset_next_day[0]
            create_report = False
        except IndexError:
            create_report = True
        context['create'] = create_report
        context['balance'] = BALANCE
        context['revenue'] = REVENUE
        context['bank'] = BANK
        
        return context

    def get(self, request, *args, **kwargs):
        self.shop = get_object_or_404(Shop, id=self.kwargs['pk'])
        if self.request.user.first_name == self.shop.name\
                                        or self.request.user.is_superuser:
            try:

                return super().get(request, *args, **kwargs)

            except ValueError:

                return HttpResponseRedirect(reverse('finance:select-report',
                                                    args=(self.kwargs['pk'],)))
        
        else:
            
            return HttpResponseRedirect(reverse('finance:no-access'))

    def form_valid(self, form):
        if form.cleaned_data['cost'].id == BANK:
            bank = BankTransaction.objects.create(
                        date=form.cleaned_data['date'] + timedelta(days=1),
                        shop=form.cleaned_data['shop'],
                        cost=form.cleaned_data['cost'],
                        amount=form.cleaned_data['amount'])
        elif form.cleaned_data['cost'].cost_type.id == SALARY\
             and form.cleaned_data['counterparty']:
            salary = Payroll.objects.create(
                        date=form.cleaned_data['date'],
                        shop=form.cleaned_data['shop'],
                        salary_type=form.cleaned_data['cost'],
                        amount=form.cleaned_data['amount'],
                        name=form.cleaned_data['counterparty'])

        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.shop = get_object_or_404(Shop, id=self.kwargs['pk'])
        if self.request.is_ajax():
            cost_type = request.POST.get('type')
            costs = Cost.objects.filter(cost_type__id=cost_type,
                                        active=True).values('id', 'name')
            counterparty_group = get_object_or_404(CostType, id=cost_type)\
                                                  .counterparty
            counterparties = Counterparty.objects.filter(group=counterparty_group,
                                                         active=True)\
                                                 .values('id', 'name')
            data = {"costs": list(costs), "counterparty": list(counterparties)}

            return HttpResponse(json.dumps(data))

        else:

            return super().post(request, *args, **kwargs)


# This view renders a form to edit the items of shop's daily report.
class ReportEditView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    template_name='finance/edit_form.html'
    model = ShopCash
    fields = ['cost', 'amount', 'counterparty', 'comment', 'shop', 'date']

    def form_valid(self, form):
        self.object = self.get_object()
        self.success_url = reverse('finance:report-view',
                                    args=(self.object.shop.id,
                                          self.object.date.year,
                                          self.object.date.month,
                                          self.object.date.day,))
        if form.cleaned_data['cost'].id == BANK:
            bank = BankTransaction.objects.filter(
                        date=form.cleaned_data['date'] + timedelta(days=1),
                        shop=form.cleaned_data['shop'],
                        cost=form.cleaned_data['cost'])\
                                          .update(
                        amount=form.cleaned_data['amount'])
        elif form.cleaned_data['cost'].cost_type.id == SALARY:
            report_item = ShopCash.objects.get(id=self.kwargs['pk'])
            salary = Payroll.objects.filter(
                        date=report_item.date,
                        shop=report_item.shop,
                        salary_type=report_item.cost,
                        amount=report_item.amount,
                        name=report_item.counterparty)\
                            .update(
                        salary_type=form.cleaned_data['cost'],
                        amount=form.cleaned_data['amount'],
                        name=form.cleaned_data['counterparty'])                            

        return super().form_valid(form)


# This view renders a form to delete the items of shop's daily report.
class ReportDeleteView(LoginRequiredMixin, DeleteView):
    login_url = '/login/'
    template_name='finance/delete_form.html'
    model = ShopCash

    def get_object(self, queryset=None):
        self.object = super().get_object()
        self.success_url = reverse('finance:report-view',
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
        context['success'] = f"/finance/{shop}/report/{year}/{month}/{day}"

        return context

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.cost.id == BANK:
            bank = BankTransaction.objects.filter(
                                    date=obj.date + timedelta(days=1),
                                    shop=obj.shop,
                                    cost=obj.cost,
                                    amount=obj.amount)\
                                          .delete()

        elif obj.cost.cost_type.id == SALARY:
            salary = Payroll.objects.filter(date=obj.date,
                                            shop=obj.shop,
                                            salary_type=obj.cost,
                                            amount=obj.amount,
                                            name=obj.counterparty)\
                                    .delete()

        return self.delete(request, *args, **kwargs)


# This view fixes closing day balance of shop's daily report.
class ReportCompleteView(LoginRequiredMixin, RedirectView):
    login_url = '/login/'

    def post(self, request, *args, **kwargs):
        self.shop = get_object_or_404(Shop, id=self.kwargs['pk'])
        self.day = date(self.kwargs['year'],
                        self.kwargs['month'],
                        self.kwargs['day'])
        self.cost = get_object_or_404(Cost, id=BALANCE)
        closing_balance = request.POST.get('closing-balance')
        fix_balance = ShopCash.objects.create(date=self.day+timedelta(days=1),
                                              shop=self.shop,
                                              cost=self.cost,
                                              amount=float(closing_balance))
        if self.request.user.is_superuser:
            self.url = reverse('finance:shop-detail',
                            args=(self.kwargs['pk'], 0,))
        else:    
            self.url = reverse('finance:greeting')

        return self.get(request, *args, **kwargs)


# This view renders a template with form to chose date of the bank transactions.
class SelectBankView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name='finance/bank_select.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
    
            return super().get(request, *args, **kwargs)
        
        else:
            
            return HttpResponseRedirect(reverse('finance:no-access'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        accounts = BankAccount.objects.filter(active=True)
        max_date = BankTransaction.objects.filter(account=accounts[0],
                                                  cost__id=BALANCE)\
                                          .aggregate(Max('date'))
        if max_date['date__max'] is None:
            message = "There are no reports."
            data = {'message': message}
        else:
            previous_day = max_date['date__max'] - timedelta(days=1)
            data = {'date': previous_day}
        context['data'] = data
        
        return context

    def post(self, request, **kwargs):
        report_date = request.POST.get('day')
        try:
            valid_date = datetime.strptime(report_date, "%Y-%m-%d")
            year = valid_date.year
            month = valid_date.month
            day = valid_date.day
           
            return HttpResponseRedirect(reverse('finance:bank-view',
                                                args=(year, month, day,)))
        
        except ValueError:

            return self.render_to_response(self.get_context_data(**kwargs))


# This view renders a form to enter the items of bank's daily report and
# a table with saved bank transactions.
class BankView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    template_name='finance/bank_form.html'
    model = BankTransaction
    fields = ['cost', 'account', 'amount', 'shop', 'counterparty', 'comment', 'date']

    def get_initial(self):
        self.day = date(self.kwargs['year'],
                        self.kwargs['month'],
                        self.kwargs['day'])
        self.initial = {'date': self.day}
        self.success_url = reverse('finance:bank-view', args=(self.kwargs['year'],
                                                             self.kwargs['month'],
                                                             self.kwargs['day'],))

        return self.initial.copy()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shops'] = Shop.objects.all()
        context['day'] = self.day
        context['cost'] = CostType.objects.all()
        data = []
        accounts = BankAccount.objects.filter(active=True)
        for account in accounts:
            bank = BankTransaction.objects.filter(date=self.day,
                                                  account=account)\
                                          .order_by('cost__cost_type')
            data.append({'name': account, 'transactions': bank})
        context['data'] = data
        no_account = BankTransaction.objects.filter(date=self.day,
                                                    account=None)\
                                            .order_by('cost__cost_type')
        context['no_accounts'] = no_account

        return context

    def get(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            try:

                return super().get(request, *args, **kwargs)

            except ValueError:

                return HttpResponseRedirect(reverse('finance:select-bank'))
        
        else:
            
            return HttpResponseRedirect(reverse('finance:no-access'))

    def post(self, request, *args, **kwargs):
        if self.request.is_ajax():
            if request.POST.get('type'):
                cost_type = request.POST.get('type')
                costs = Cost.objects.filter(cost_type__id=cost_type,
                                            active=True).values('id', 'name')
                counterparty_group = get_object_or_404(CostType, id=cost_type)\
                                                    .counterparty
                counterparties = Counterparty.objects.filter(
                                        group=counterparty_group,
                                        active=True).values('id', 'name')
                data = {"costs": list(costs),
                        "counterparty": list(counterparties)}
            elif request.POST.get('account'):
                account_id = request.POST.get('account')
                account = get_object_or_404(BankAccount, id=account_id)
                cost = get_object_or_404(Cost, id=BALANCE)
                closing_balance = float(request.POST.get('balance'))
                next_open_balance = BankTransaction.objects.get_or_create(
                                date=date(self.kwargs['year'],
                                          self.kwargs['month'],
                                          self.kwargs['day'])\
                                     + timedelta(days=1),
                                account=account,
                                cost=cost,
                                defaults={'amount': closing_balance},)
                if next_open_balance[1] == False:
                    setattr(next_open_balance[0], 'amount', closing_balance)
                    next_open_balance[0].save()
                data = {"success": True}

            return HttpResponse(json.dumps(data))

        else:

            return super().post(request, *args, **kwargs)


# This view renders a form to edit the bank daily report.
class BankEditView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    template_name='finance/bank_edit_form.html'
    model = BankTransaction
    fields = ['date', 'account', 'cost', 'amount',
              'counterparty', 'shop', 'comment']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        year = self.object.date.year
        month = self.object.date.month
        day = self.object.date.day
        self.success_url = reverse('finance:bank-view',
                                   args=(year, month, day,))
        return super().post(request, *args, **kwargs)


# This view renders a form to delete the items of bank's daily report.
class BankDeleteView(LoginRequiredMixin, DeleteView):
    login_url = '/login/'
    template_name='finance/bank_delete_form.html'
    model = BankTransaction

    def get_object(self, queryset=None):
        self.object = super().get_object()
        self.success_url = reverse('finance:bank-view',
                                    args=(self.object.date.year,
                                          self.object.date.month,
                                          self.object.date.day,))
        return self.object   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.object.date.year
        month = self.object.date.month
        day = self.object.date.day
        context['success'] = f"../../{year}/{month}/{day}/"

        return context


class NoAccessView(TemplateView):
    template_name='finance/no_access.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = Shop.objects.get(name=self.request.user.first_name)
        context['shop'] = shop
        
        return context


class GreetingView(TemplateView):
    template_name='finance/greeting.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            shop = Shop.objects.get(name=self.request.user.first_name)
            context['shop'] = shop
        
        return context
