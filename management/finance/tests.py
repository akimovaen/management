import calendar

from datetime import date, datetime

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select

from management.settings import BALANCE, REVENUE, BANK, SALARY
from .models import *
from .views import *
from . import util

# Create your tests here.

class ShopDetailTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create_superuser('test', 'test@test.com', 'test')
        cls.today = datetime.today()
        cls.trademark = Trademark.objects.create(name="TM")
        cls.shop = Shop.objects.create(name="Shop",
                                       trademark=cls.trademark)
        cls.cost_type1 = CostType.objects.create(name="Opening day balance")
        cls.cost_type2 = CostType.objects.create(name="Revenue")
        cls.cost1 = Cost.objects.create(name="Opening day balance",
                                        cost_type=cls.cost_type1,
                                        income=True)
        cls.cost2 = Cost.objects.create(name="Total revenue",
                                        cost_type=cls.cost_type2,
                                        income=True)
        cls.cost3 = Cost.objects.create(name="Noncash revenue",
                                        cost_type=cls.cost_type2,
                                        income=True)
        cls.shopcash_item1 = ShopCash.objects.create(date=date(cls.today.year,
                                                          cls.today.month, 1),
                                                     shop=cls.shop,
                                                     cost=cls.cost1,
                                                     amount=1000)
        cls.shopcash_item2 = ShopCash.objects.create(date=date(cls.today.year,
                                                          cls.today.month, 2),
                                                     shop=cls.shop,
                                                     cost=cls.cost1,
                                                     amount=1400)
        cls.shopcash_item3 = ShopCash.objects.create(date=date(cls.today.year,
                                                          cls.today.month, 1),
                                                     shop=cls.shop,
                                                     cost=cls.cost2,
                                                     amount=2000)
        cls.shopcash_item4 = ShopCash.objects.create(date=date(cls.today.year,
                                                          cls.today.month, 1),
                                                     shop=cls.shop,
                                                     cost=cls.cost3,
                                                     amount=1600)

    def test_get_view_served_response(self):
        response = self.client.get(reverse('finance:shop-detail',
                                           args=(self.shop.id, 0)))
        self.assertEqual(response.resolver_match.func.__name__,
                         ShopDetailView.as_view().__name__)
    
    def test_get_status_code_and_template_with_user_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:shop-detail',
                                           args=(self.shop.id, 0)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/shop_month.html')

    def test_get_status_code_shop_not_found(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:shop-detail',
                                           args=(self.shop.id+1, 0)))
        self.assertEqual(response.status_code, 404)

    def test_get_status_code_without_user_login(self):
        response = self.client.get(reverse('finance:shop-detail',
                                           args=(self.shop.id, 0)))
        self.assertEqual(response.status_code, 302)

    def test_get_redirect_to_login(self):
        response = self.client.get(reverse('finance:shop-detail',
                                           args=(self.shop.id, 0)),
                                           follow=True)
        self.assertEqual(response.redirect_chain,
                         [(f'/login/?next=/finance/{self.shop.id}/0/', 302)])

    def test_get_context_data_agregate_data(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:shop-detail',
                                           args=(self.shop.id, 0)))
        self.assertEqual(len(response.context['data']), 2)
        self.assertEqual(len(response.context['data'][1].costs), 1)
        self.assertEqual(response.context['data'][1].name, "Cash revenue")
        self.assertEqual(response.context['data'][0].costs[0].days[1], 1000)
        self.assertEqual(response.context['data'][0].costs[0].days[2], 1400)
        self.assertEqual(response.context['data'][1].costs[0].days[1], 2000-1600)

    def test_get_context_data_weekdays(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:shop-detail',
                                           args=(self.shop.id, 0)))
        self.assertEqual(len(response.context['weekdays']),
                    calendar.monthrange(self.today.year, self.today.month)[1])

    def test_get_context_data_month_name(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:shop-detail',
                                           args=(self.shop.id, 0)))
        self.assertEqual(response.context['month_name'],
                         util.month_name(self.today.month))


class SeleniumTests1ShopMonth(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_superuser('test', 'test@test.com', 'test')
        cls.today = datetime.today()
        cls.trademark = Trademark.objects.create(name="TM")
        cls.shop = Shop.objects.create(name="Shop",
                                       trademark=cls.trademark)
        cls.cost_type1 = CostType.objects.create(name="Opening day balance")
        cls.cost_type2 = CostType.objects.create(name="Revenue")
        cls.cost_type3 = CostType.objects.create(name="Empty")
        cls.cost1 = Cost.objects.create(name="Opening day balance",
                                        cost_type=cls.cost_type1,
                                        income=True)
        cls.cost2 = Cost.objects.create(name="Total revenue",
                                        cost_type=cls.cost_type2,
                                        income=True)
        cls.cost3 = Cost.objects.create(name="Noncash revenue",
                                        cost_type=cls.cost_type2,
                                        income=True)
        cls.shopcash_item1 = ShopCash.objects.create(date=date(cls.today.year,
                                                          cls.today.month, 1),
                                                     shop=cls.shop,
                                                     cost=cls.cost1,
                                                     amount=1000)
        cls.shopcash_item2 = ShopCash.objects.create(date=date(cls.today.year,
                                                          cls.today.month, 2),
                                                     shop=cls.shop,
                                                     cost=cls.cost1,
                                                     amount=3000)
        cls.shopcash_item3 = ShopCash.objects.create(date=date(cls.today.year,
                                                          cls.today.month, 1),
                                                     shop=cls.shop,
                                                     cost=cls.cost2,
                                                     amount=3000)
        cls.shopcash_item4 = ShopCash.objects.create(date=date(cls.today.year,
                                                          cls.today.month, 1),
                                                     shop=cls.shop,
                                                     cost=cls.cost3,
                                                     amount=1000)
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.cache.disk.enable", False)
        profile.set_preference("browser.cache.memory.enable", False)
        profile.set_preference("browser.cache.offline.enable", False)
        profile.set_preference("network.http.use-cache", False)
        cls.selenium = webdriver.Firefox(profile)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_shop_month(self):
        # Test LoginRequiredMixin.
        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse('finance:shop-detail',
                                            args=(self.shop.id, 0))))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('test')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('test')
        self.selenium.find_element_by_class_name('btn').click()
        self.assertEqual("Shop", self.selenium.title)

        # Check total amount of cost types per day.
        types_list = self.selenium.find_elements_by_class_name('type_totals')
        self.assertEqual(len(types_list), 3)
        open_balance1 = types_list[0].find_element_by_class_name('day-1')
        self.assertEqual(open_balance1.text, '1000.00')
        open_balance2 = types_list[0].find_element_by_class_name('day-2')
        self.assertEqual(open_balance2.text, '3000.00')
        cash_revenue = types_list[1].find_element_by_class_name('day-1')
        self.assertEqual(cash_revenue.text, '2000.00')

        # Check closing day balance per day.
        closing_balance = self.selenium.find_element_by_class_name('closing_balance')
        close_balance1 = closing_balance.find_element_by_class_name('day-1')
        self.assertEqual(close_balance1.text, '3000.00')
        close_balance2 = closing_balance.find_element_by_class_name('day-2')
        self.assertEqual(close_balance2.text, '3000.00')


class SelectReportTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.trademark = Trademark.objects.create(name="TM")
        cls.shop = Shop.objects.create(name="Shop",
                                       trademark=cls.trademark)
        cls.cost_type = CostType.objects.create(name="Opening day balance")
        cls.cost = Cost.objects.create(name="Opening day balance",
                                       cost_type=cls.cost_type,
                                       income=True)
        cls.user = User.objects.create_superuser('test', 'test@test.com', 'test')
        cls.client = Client()

    def test_get_view_served_response(self):
        response = self.client.get(reverse('finance:select-report',
                                           args=(self.shop.id,)))
        self.assertEqual(response.resolver_match.func.__name__,
                         SelectReportView.as_view().__name__)
    
    def test_get_status_code_and_template_with_user_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:select-report',
                                           args=(self.shop.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/report_select.html')

    def test_get_status_code_shop_not_found(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:select-report',
                                           args=(self.shop.id+1,)))
        self.assertEqual(response.status_code, 404)

    def test_get_status_code_without_user_login(self):
        response = self.client.get(reverse('finance:select-report',
                                           args=(self.shop.id,)))
        self.assertEqual(response.status_code, 302)

    def test_get_redirect_to_login(self):
        response = self.client.get(reverse('finance:select-report',
                                           args=(self.shop.id,)),
                                           follow=True)
        self.assertEqual(response.redirect_chain,
               [(f'/login/?next=/finance/{self.shop.id}/report/select/', 302)])

    def test_get_context_data_shop(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:select-report',
                                           args=(self.shop.id,)))
        self.assertEqual(response.context['shop'].name, self.shop.name)
        self.assertEqual(response.context['shop'].id, self.shop.id)

    def test_get_context_data_report_not_completed(self):
        shopcash_item = ShopCash.objects.create(date=date(2020,1,2),
                                                shop=self.shop,
                                                cost=self.cost,
                                                amount=1000)
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:select-report',
                                           args=(self.shop.id,)))
        self.assertEqual(response.context['message'],
                         "Report from 2020-01-02 is not completed")

    def test_get_context_data_no_reports(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:select-report',
                                           args=(self.shop.id,)))
        self.assertEqual(response.context['message'],
                         "There are no reports.")

    def test_get_context_data_last_report_date(self):
        shopcash_item1 = ShopCash.objects.create(date=date(2020,1,1),
                                                shop=self.shop,
                                                cost=self.cost,
                                                amount=1000)
        shopcash_item2 = ShopCash.objects.create(date=date(2020,1,2),
                                                shop=self.shop,
                                                cost=self.cost,
                                                amount=1000)
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:select-report',
                                           args=(self.shop.id,)))
        self.assertEqual(response.context['last_report_date'], date(2020,1,1))

    def test_post_valid_day(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:select-report',
                                           args=(self.shop.id,)),
                                   {'day':"2020-01-31"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
                         f'/finance/{self.shop.id}/report/2020/1/31/')
        
    def test_post_invalid_day(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:select-report',
                                           args=(self.shop.id,)),
                                   {'day':"2020-01-32"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/report_select.html')


class CreateReportTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create_superuser('test', 'test@test.com', 'test')
        cls.trademark = Trademark.objects.create(name="TM")
        cls.shop = Shop.objects.create(name="Shop",
                                       trademark=cls.trademark)
        cls.cost_type1 = CostType.objects.create(name="Opening day balance")
        cls.cost_type2 = CostType.objects.create(name="Revenue")
        cls.cost1 = Cost.objects.create(name="Opening day balance",
                                       cost_type=cls.cost_type1,
                                       income=True)
        cls.cost2 = Cost.objects.create(name="Total revenue",
                                       cost_type=cls.cost_type2,
                                       income=True)
        cls.cost3 = Cost.objects.create(name="Noncash revenue",
                                       cost_type=cls.cost_type2,
                                       income=True)
    
    def test_get_view_served_response(self):
        response = self.client.get(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)))
        self.assertEqual(response.resolver_match.func.__name__,
                         ReportCreateView.as_view().__name__)

    def test_get_status_code_and_template_with_user_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/report_form.html')

    def test_get_status_code_without_user_login(self):
        response = self.client.get(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)))
        self.assertEqual(response.status_code, 302)

    def test_get_redirect_to_login(self):
        response = self.client.get(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)),
                                   follow=True)
        self.assertEqual(response.redirect_chain,
             [(f'/login/?next=/finance/{self.shop.id}/report/2020/1/1/', 302)])

    def test_get_context_data_valid_shop(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)))
        self.assertEqual(response.context['shop'].name, self.shop.name)
        self.assertEqual(response.context['shop'].id, self.shop.id)

    def test_get_context_data_invalid_shop(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:report-view',
                                           args=(self.shop.id+1, 2020, 1, 1)))
        self.assertEqual(response.status_code, 404)

    def test_get_context_data_valid_day(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)))
        self.assertEqual(response.context['day'], date(2020, 1, 1))

    def test_get_context_data_invalid_day(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 32)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
                         f'/finance/{self.shop.id}/report/select/')

    def test_get_context_data_create_true(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)))
        self.assertTrue(response.context['create'])

    def test_get_context_data_create_false(self):
        self.client.force_login(self.user)
        shopcash_item = ShopCash.objects.create(date=date(2020, 1, 2),
                                                shop=self.shop,
                                                cost=self.cost1,
                                                amount=1000)
        response = self.client.get(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)))
        self.assertFalse(response.context['create'])

    def test_get_context_data_empty_data(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)))
        self.assertEqual(len(response.context['data']), 0)

    def test_get_context_data_exist_data(self):
        self.client.force_login(self.user)
        shopcash_item = ShopCash.objects.create(date=date(2020, 1, 1),
                                                shop=self.shop,
                                                cost=self.cost1,
                                                amount=1000)
        response = self.client.get(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)))
        self.assertEqual(len(response.context['data']), 1)

    def test_post_valid_data(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)),
                                    {'date': date(2020, 1, 1),
                                     'shop': self.shop.id,
                                     'cost': self.cost1.id,
                                     'amount': 1000})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
                         f'/finance/{self.shop.id}/report/2020/1/1/')

    def test_post_noncash(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)),
                                    {'date': date(2020, 1, 1),
                                     'shop': self.shop.id,
                                     'cost': self.cost3.id,
                                     'amount': 200})
        self.assertEqual(response.status_code, 302)
        bank = BankTransaction.objects.filter(date=date(2020, 1, 2))
        self.assertEqual(len(bank), 1)

    def test_post_invalid_cost(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)),
                                    {'date': date(2020, 1, 1),
                                     'shop': self.shop.id,
                                     'cost': self.cost3.id+1,
                                     'amount': 1000})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/report_form.html')

    def test_post_invalid_amount(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)),
                                    {'date': date(2020, 1, 1),
                                     'shop': self.shop.id,
                                     'cost': self.cost1.id,
                                     'amount': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/report_form.html')


@override_settings(BALANCE=4, REVENUE=5, BANK=6)
class SeleniumTests2ReportForm(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_superuser('test', 'test@test.com', 'test')
        cls.trademark = Trademark.objects.create(name="TM")
        cls.shop = Shop.objects.create(name="Shop",
                                       trademark=cls.trademark)
        cls.cost_type1 = CostType.objects.create(name="Opening day balance")
        cls.cost_type2 = CostType.objects.create(name="Revenue")
        cls.cost_type3 = CostType.objects.create(name="Empty")
        cls.cost1 = Cost.objects.create(name="Opening day balance",
                                       cost_type=cls.cost_type1,
                                       income=True)
        cls.cost2 = Cost.objects.create(name="Total revenue",
                                       cost_type=cls.cost_type2,
                                       income=True)
        cls.cost3 = Cost.objects.create(name="Noncash revenue",
                                       cost_type=cls.cost_type2,
                                       income=True)
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.cache.disk.enable", False)
        profile.set_preference("browser.cache.memory.enable", False)
        profile.set_preference("browser.cache.offline.enable", False)
        profile.set_preference("network.http.use-cache", False)
        cls.selenium = webdriver.Firefox(profile)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_report_form(self):
        # Test LoginRequiredMixin.
        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 2))))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('test')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('test')
        self.selenium.find_element_by_class_name('btn').click()
        self.assertEqual("Report", self.selenium.title)

        self.selenium.find_element_by_xpath('//button[@id="add-data"]').click()

        # Test the ajax-request.
        cost_type_input = self.selenium.find_element_by_id('cost_type')
        cost_type_select = Select(cost_type_input)
        cost_type_select.select_by_value(str(self.cost_type1.id))
        cost_input = self.selenium.find_element_by_id('id_cost')
        cost_select = Select(cost_input)
        self.assertEqual(1, len(cost_select.options)-1)

        cost_type_select.select_by_value(str(self.cost_type2.id))
        cost_input = self.selenium.find_element_by_id('id_cost')
        cost_select = Select(cost_input)
        self.assertEqual(2, len(cost_select.options)-1)

        # Test sending the form.
        cost_type_input = self.selenium.find_element_by_id('cost_type')
        cost_type_select = Select(cost_type_input)
        cost_type_select.select_by_value(str(self.cost_type1.id))
        cost_input = self.selenium.find_element_by_id('id_cost')
        cost_select = Select(cost_input)
        cost_select.select_by_value(str(self.cost1.id))
        amount_input = self.selenium.find_element_by_id('id_amount')
        amount_input.send_keys('1000')
        self.selenium.find_element_by_xpath('//input[@value="Ready"]').click()

        # Check the data in the table.
        cost_name = f'item-{self.cost1.id}'
        table_data_1 = self.selenium.find_element_by_class_name(cost_name)
        data_1_amount = table_data_1.find_element_by_class_name('amount')
        self.assertEqual('1000.00', data_1_amount.text)
        total_income = self.selenium.find_element_by_id('total-income')
        self.assertEqual('1000.00', total_income.text)
        total_outcome = self.selenium.find_element_by_id('total-expense')
        self.assertEqual('0.00', total_outcome.text)
        closing_balance = self.selenium.find_element_by_id('closing-balance')
        self.assertEqual('1000.00', closing_balance.text)

        # Test editing data in the table.
        table_data_1.find_element_by_class_name('edit').click()
        edit_data_1_amount = self.selenium.find_element_by_id('id_amount')
        edit_data_1_amount.clear()
        edit_data_1_amount.send_keys('900')
        self.selenium.find_element_by_xpath('//input[@value="Edit"]').click()

        # Check the data in the table.
        table_data_1 = self.selenium.find_element_by_class_name(cost_name)
        data_1_amount = table_data_1.find_element_by_class_name('amount')
        self.assertEqual('900.00', data_1_amount.text)
        total_income = self.selenium.find_element_by_id('total-income')
        self.assertEqual('900.00', total_income.text)
        closing_balance = self.selenium.find_element_by_id('closing-balance')
        self.assertEqual('900.00', closing_balance.text)

        # Test deleting data in the table.
        table_data_1.find_element_by_class_name('delete').click()
        self.selenium.find_element_by_xpath('//input[@value="Delete"]').click()

        # Check empty table.
        assert "<table>" not in self.selenium.page_source


class EditReportTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create_superuser('test', 'test@test.com', 'test')
        cls.trademark = Trademark.objects.create(name="TM")
        cls.shop = Shop.objects.create(name="Shop",
                                       trademark=cls.trademark)
        cls.cost_type1 = CostType.objects.create(name="Opening day balance")
        cls.cost_type2 = CostType.objects.create(name="Revenue")
        cls.cost1 = Cost.objects.create(name="Opening day balance",
                                       cost_type=cls.cost_type1,
                                       income=True)
        cls.cost2 = Cost.objects.create(name="Total revenue",
                                       cost_type=cls.cost_type2,
                                       income=True)
        cls.cost3 = Cost.objects.create(name="Noncash revenue",
                                       cost_type=cls.cost_type2,
                                       income=True)
        cls.shopcash_item = ShopCash.objects.create(date=date(2020, 1, 1),
                                                    shop=cls.shop,
                                                    cost=cls.cost1,
                                                    amount=1000)
        
    def test_get_view_served_response(self):
        response = self.client.get(reverse('finance:report-edit',
                                            args=(self.shopcash_item.id,)))
        self.assertEqual(response.resolver_match.func.__name__,
                         ReportEditView.as_view().__name__)

    def test_get_status_code_and_template_with_user_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:report-edit',
                                            args=(self.shopcash_item.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/edit_form.html')

    def test_get_status_code_without_user_login(self):
        response = self.client.get(reverse('finance:report-edit',
                                            args=(self.shopcash_item.id,)))
        self.assertEqual(response.status_code, 302)

    def test_get_redirect_to_login(self):
        response = self.client.get(reverse('finance:report-edit',
                                            args=(self.shopcash_item.id,)),
                                   follow=True)
        self.assertEqual(response.redirect_chain,
                         [('/login/?next=/finance/report/edit/1/', 302)])

    def test_get_valid_shopcash(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:report-edit',
                                            args=(self.shopcash_item.id,)))
        self.assertEqual(response.context['object'].shop.name, self.shop.name)
        self.assertEqual(response.context['object'].date, date(2020, 1, 1))
        self.assertEqual(response.context['object'].cost.name, self.cost1.name)
        self.assertEqual(response.context['object'].amount, 1000)

    def test_get_invalid_shopcash(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:report-edit',
                                            args=(self.shopcash_item.id+1,)))
        self.assertEqual(response.status_code, 404)

    def test_post_valid_data(self):
        self.client.force_login(self.user)
        response_view = self.client.get(reverse('finance:report-view',
                                            args=(self.shop.id, 2020, 1, 1)))
        self.assertEqual(response_view.context['data'][0].amount, 1000)
        response_edit = self.client.post(reverse('finance:report-edit',
                                            args=(self.shopcash_item.id,)),
                                    {'date': date(2020, 1, 1), 
                                     'shop': self.shop.id,
                                     'cost': self.cost1.id,
                                     'amount': 900})
        self.assertEqual(response_edit.status_code, 302)
        self.assertEqual(response_edit.url,
                         f'/finance/{self.shop.id}/report/2020/1/1/')
        response_view = self.client.get(reverse('finance:report-view',
                                            args=(self.shop.id, 2020, 1, 1)))
        self.assertEqual(response_view.context['data'][0].amount, 900)

    def test_post_invalid_cost(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:report-edit',
                                            args=(self.shopcash_item.id,)),
                                    {'date': date(2020, 1, 1),
                                     'shop': self.shop.id,
                                     'cost': self.cost3.id+1,
                                     'amount': 1000})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/edit_form.html')

    def test_post_invalid_amount(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:report-edit',
                                            args=(self.shopcash_item.id,)),
                                    {'date': date(2020, 1, 1),
                                     'shop': self.shop.id,
                                     'cost': self.cost1,
                                     'amount': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/edit_form.html')

    def test_post_noncash(self):
        self.client.force_login(self.user)
        response_view = self.client.post(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)),
                                    {'date': date(2020, 1, 1),
                                     'shop': self.shop.id,
                                     'cost': self.cost3.id,
                                     'amount': 200})
        bank = BankTransaction.objects.filter(date=date(2020, 1, 2))
        self.assertEqual(bank[0].amount, 200)
        shopcash = ShopCash.objects.get(date=date(2020, 1, 1),
                                        shop=self.shop,
                                        cost=self.cost3,
                                        amount=200)
        response_edit = self.client.post(reverse('finance:report-edit',
                                            args=(shopcash.id,)),
                                    {'date': date(2020, 1, 1),
                                     'shop': self.shop.id,
                                     'cost': self.cost3.id,
                                     'amount': 250})
        self.assertEqual(response_edit.status_code, 302)
        bank = BankTransaction.objects.filter(date=date(2020, 1, 2))
        self.assertEqual(bank[0].amount, 250)


class DeleteReportTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create_superuser('test', 'test@test.com', 'test')
        cls.trademark = Trademark.objects.create(name="TM")
        cls.shop = Shop.objects.create(name="Shop",
                                       trademark=cls.trademark)
        cls.cost_type1 = CostType.objects.create(name="Opening day balance")
        cls.cost_type2 = CostType.objects.create(name="Revenue")
        cls.cost1 = Cost.objects.create(name="Opening day balance",
                                       cost_type=cls.cost_type1,
                                       income=True)
        cls.cost2 = Cost.objects.create(name="Total revenue",
                                       cost_type=cls.cost_type2,
                                       income=True)
        cls.cost3 = Cost.objects.create(name="Noncash revenue",
                                       cost_type=cls.cost_type2,
                                       income=True)
        cls.shopcash_item = ShopCash.objects.create(date=date(2020, 1, 1),
                                                    shop=cls.shop,
                                                    cost=cls.cost1,
                                                    amount=1000)
        
    def test_get_view_served_response(self):
        response = self.client.get(reverse('finance:report-delete',
                                            args=(self.shopcash_item.id,)))
        self.assertEqual(response.resolver_match.func.__name__,
                         ReportDeleteView.as_view().__name__)

    def test_get_status_code_and_template_with_user_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:report-delete',
                                            args=(self.shopcash_item.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/delete_form.html')

    def test_get_status_code_without_user_login(self):
        response = self.client.get(reverse('finance:report-delete',
                                            args=(self.shopcash_item.id,)))
        self.assertEqual(response.status_code, 302)

    def test_get_redirect_to_login(self):
        response = self.client.get(reverse('finance:report-delete',
                                            args=(self.shopcash_item.id,)),
                                   follow=True)
        self.assertEqual(response.redirect_chain,
             [(f'/login/?next=/finance/report/delete/{self.shopcash_item.id}/',
              302)])

    def test_get_valid_shopcash(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:report-delete',
                                            args=(self.shopcash_item.id,)))
        self.assertEqual(response.context['object'].shop.name, self.shop.name)
        self.assertEqual(response.context['object'].date, date(2020, 1, 1))
        self.assertEqual(response.context['object'].cost.name, self.cost1.name)
        self.assertEqual(response.context['object'].amount, 1000)

    def test_get_invalid_shopcash(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:report-delete',
                                            args=(self.shopcash_item.id+1,)))
        self.assertEqual(response.status_code, 404)

    def test_post_data(self):
        self.client.force_login(self.user)
        response_view = self.client.get(reverse('finance:report-view',
                                            args=(self.shop.id, 2020, 1, 1)))
        self.assertEqual(response_view.context['data'][0].amount, 1000)
        response_delete = self.client.post(reverse('finance:report-delete',
                                               args=(self.shopcash_item.id,)),
                                    {'date': date(2020, 1, 1),
                                     'shop': self.shop.id,
                                     'cost': self.cost1,
                                     'amount': 1000})
        self.assertEqual(response_delete.status_code, 302)
        self.assertEqual(response_delete.url,
                         f'/finance/{self.shop.id}/report/2020/1/1/')
        response_view = self.client.get(reverse('finance:report-view',
                                            args=(self.shop.id, 2020, 1, 1)))
        self.assertEqual(len(response_view.context['data']), 0)

    def test_post_noncash(self):
        self.client.force_login(self.user)
        response_view = self.client.post(reverse('finance:report-view',
                                           args=(self.shop.id, 2020, 1, 1)),
                                    {'date': date(2020, 1, 1),
                                     'shop': self.shop.id,
                                     'cost': self.cost3.id,
                                     'amount': 200})
        bank = BankTransaction.objects.filter(date=date(2020, 1, 2))
        self.assertEqual(len(bank), 1)
        shopcash = ShopCash.objects.get(date=date(2020, 1, 1),
                                        shop=self.shop,
                                        cost=self.cost3,
                                        amount=200)
        response_delete = self.client.post(reverse('finance:report-delete',
                                            args=(shopcash.id,)))
        self.assertEqual(response_delete.status_code, 302)
        bank = BankTransaction.objects.filter(date=date(2020, 1, 2))
        self.assertFalse(bank)


class SelectBankTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account = BankAccount.objects.create(name="Mr.Smith")
        cls.trademark = Trademark.objects.create(name="TM")
        cls.shop = Shop.objects.create(name="Shop",
                                       trademark=cls.trademark)
        cls.cost_type = CostType.objects.create(name="Opening day balance")
        cls.cost = Cost.objects.create(name="Opening day balance",
                                       cost_type=cls.cost_type,
                                       income=True)
        cls.user = User.objects.create_superuser('test', 'test@test.com', 'test')
        cls.client = Client()

    def test_get_view_served_response(self):
        response = self.client.get(reverse('finance:select-bank'))
        self.assertEqual(response.resolver_match.func.__name__,
                         SelectBankView.as_view().__name__)
    
    def test_get_status_code_and_template_with_user_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:select-bank'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/bank_select.html')

    def test_get_status_code_without_user_login(self):
        response = self.client.get(reverse('finance:select-bank'))
        self.assertEqual(response.status_code, 302)

    def test_get_redirect_to_login(self):
        response = self.client.get(reverse('finance:select-bank'),
                                   follow=True)
        self.assertEqual(response.redirect_chain,
               [('/login/?next=/finance/bank/select/', 302)])

    def test_get_context_data_no_transactions(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:select-bank'))
        self.assertEqual(response.context['data']['message'],
                         "There are no reports.")

    def test_get_context_data_last_transaction_date(self):
        bank_item1 = BankTransaction.objects.create(date=date(2020,1,1),
                                                    account=self.account,
                                                    shop=self.shop,
                                                    cost=self.cost,
                                                    amount=1000)
        bank_item2 = BankTransaction.objects.create(date=date(2020,1,2),
                                                    account=self.account,
                                                    shop=self.shop,
                                                    cost=self.cost,
                                                    amount=1000)
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:select-bank'))
        self.assertEqual(response.context['data']['date'], date(2020,1,1))

    def test_post_valid_day(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:select-bank'),
                                   {'day':"2020-01-31"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/finance/bank/2020/1/31/')
        
    def test_post_invalid_day(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:select-bank'),
                                   {'day':"2020-01-32"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/bank_select.html')


class BankTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account1 = BankAccount.objects.create(name="Mr.Smith")
        cls.account2 = BankAccount.objects.create(name="Ms.Smith")
        cls.client = Client()
        cls.user = User.objects.create_superuser('test', 'test@test.com', 'test')
        cls.trademark = Trademark.objects.create(name="TM")
        cls.shop = Shop.objects.create(name="Shop",
                                       trademark=cls.trademark)
        cls.cost_type1 = CostType.objects.create(name="Opening day balance")
        cls.cost_type2 = CostType.objects.create(name="Revenue")
        cls.cost1 = Cost.objects.create(name="Opening day balance",
                                       cost_type=cls.cost_type1,
                                       income=True)
        cls.cost2 = Cost.objects.create(name="Total revenue",
                                       cost_type=cls.cost_type2,
                                       income=True)
        cls.cost3 = Cost.objects.create(name="Noncash revenue",
                                       cost_type=cls.cost_type2,
                                       income=True)
    
    def test_get_view_served_response(self):
        response = self.client.get(reverse('finance:bank-view',
                                           args=(2020, 1, 1)))
        self.assertEqual(response.resolver_match.func.__name__,
                         BankView.as_view().__name__)

    def test_get_status_code_and_template_with_user_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:bank-view',
                                           args=(2020, 1, 1)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/bank_form.html')

    def test_get_status_code_without_user_login(self):
        response = self.client.get(reverse('finance:bank-view',
                                           args=(2020, 1, 1)))
        self.assertEqual(response.status_code, 302)

    def test_get_redirect_to_login(self):
        response = self.client.get(reverse('finance:bank-view',
                                           args=(2020, 1, 1)),
                                   follow=True)
        self.assertEqual(response.redirect_chain,
             [('/login/?next=/finance/bank/2020/1/1/', 302)])

    def test_get_context_data_valid_day(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:bank-view',
                                           args=(2020, 1, 31)))
        self.assertEqual(response.context['day'], date(2020, 1, 31))

    def test_get_context_data_invalid_day(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:bank-view',
                                           args=(2020, 1, 32)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/finance/bank/select/')

    def test_get_context_data_empty_data(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:bank-view',
                                           args=(2020, 1, 1)))
        self.assertEqual(len(response.context['data'][0]['transactions']), 0)
        self.assertEqual(len(response.context['data'][1]['transactions']), 0)

    def test_get_context_data_exist_data(self):
        self.client.force_login(self.user)
        bank_item1 = BankTransaction.objects.create(date=date(2020,1,1),
                                                    account=self.account1,
                                                    shop=self.shop,
                                                    cost=self.cost1,
                                                    amount=1000)
        bank_item2 = BankTransaction.objects.create(date=date(2020,1,1),
                                                    account=self.account2,
                                                    shop=self.shop,
                                                    cost=self.cost1,
                                                    amount=1000)
        response = self.client.get(reverse('finance:bank-view',
                                           args=(2020, 1, 1)))
        self.assertEqual(len(response.context['data'][0]['transactions']), 1)
        self.assertEqual(len(response.context['data'][1]['transactions']), 1)

    def test_get_context_data_no_accounts(self):
        self.client.force_login(self.user)
        bank_item = BankTransaction.objects.create(date=date(2020,1,1),
                                                   shop=self.shop,
                                                   cost=self.cost3,
                                                   amount=1000)
        response = self.client.get(reverse('finance:bank-view',
                                           args=(2020, 1, 1)))
        self.assertEqual(len(response.context['no_accounts']), 1)

    def test_post_valid_data(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:bank-view',
                                            args=(2020, 1, 1)),
                                    {'date': date(2020, 1, 1),
                                     'account': self.account1.id,
                                     'cost': self.cost1.id,
                                     'amount': 1000})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/finance/bank/2020/1/1/')
        open_balance = BankTransaction.objects.get(date=date(2020, 1, 1),
                                                      account=self.account1,
                                                      cost=self.cost1)
        self.assertEqual(open_balance.amount, 1000)

    def test_post_invalid_account(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:bank-view',
                                            args=(2020, 1, 1)),
                                    {'date': date(2020, 1, 1),
                                     'account': self.account2.id+1,
                                     'cost': self.cost1.id,
                                     'amount': 1000})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/bank_form.html')

    def test_post_invalid_cost(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:bank-view',
                                            args=(2020, 1, 1)),
                                    {'date': date(2020, 1, 1),
                                     'account': self.account1.id,
                                     'cost': self.cost3.id+1,
                                     'amount': 1000})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/bank_form.html')

    def test_post_invalid_amount(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:bank-view',
                                            args=(2020, 1, 1)),
                                    {'date': date(2020, 1, 1),
                                     'account': self.account1.id,
                                     'cost': self.cost1.id,
                                     'amount': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/bank_form.html')


@override_settings(BALANCE=7, REVENUE=8, BANK=9)
class SeleniumTests3BankForm(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_superuser('test', 'test@test.com', 'test')
        cls.account = BankAccount.objects.create(name="Account1")
        cls.trademark = Trademark.objects.create(name="TM")
        cls.shop = Shop.objects.create(name="Shop",
                                       trademark=cls.trademark)
        cls.cost_type = CostType.objects.create(name="Opening day balance")
        cls.cost = Cost.objects.create(name="Opening day balance",
                                       cost_type=cls.cost_type,
                                       income=True)
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.cache.disk.enable", False)
        profile.set_preference("browser.cache.memory.enable", False)
        profile.set_preference("browser.cache.offline.enable", False)
        profile.set_preference("network.http.use-cache", False)
        cls.selenium = webdriver.Firefox(profile)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_bank_form(self):
        # Test LoginRequiredMixin.
        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse('finance:bank-view',
                                           args=(2020, 1, 1))))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('test')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('test')
        self.selenium.find_element_by_class_name('btn').click()
        self.assertEqual("Bank", self.selenium.title)

        self.selenium.find_element_by_xpath('//button[@id="add-data"]').click()

        # Test the ajax-request with cost type.
        cost_type_input = self.selenium.find_element_by_id('cost_type')
        cost_type_select = Select(cost_type_input)
        cost_type_select.select_by_value(str(self.cost_type.id))
        cost_input = self.selenium.find_element_by_id('id_cost')
        cost_select = Select(cost_input)
        self.assertEqual(1, len(cost_select.options)-1)

        # Test sending the form.
        cost_select.select_by_value(str(self.cost.id))
        account_input = self.selenium.find_element_by_id('id_account')
        account_select = Select(account_input)
        account_select.select_by_value(str(self.account.id))
        amount_input = self.selenium.find_element_by_id('id_amount')
        amount_input.send_keys('1000')
        self.selenium.find_element_by_xpath('//input[@value="Ready"]').click()

        # Check the data in the table.
        table = self.selenium.find_element_by_name(self.account.id)
        cost_name = f'item-{self.cost.id}'
        table_data_1 = table.find_element_by_class_name(cost_name)
        data_1_amount = table_data_1.find_element_by_class_name('income')
        self.assertEqual('1000.00', data_1_amount.text)
        total_income = table.find_element_by_class_name('total_income')
        self.assertEqual('1000.00', total_income.text)
        total_outcome = table.find_element_by_class_name('total_outcome')
        self.assertEqual('0.00', total_outcome.text)
        closing_balance = table.find_element_by_class_name('closing_balance')
        self.assertEqual('1000.00', closing_balance.text)

        # Test the ajax-request with closing balance.
        open_balance = BankTransaction.objects.get(date=date(2020, 1, 2),
                                                   account=self.account,
                                                   cost__id=BALANCE)
        self.assertEqual(1000, open_balance.amount)


class EditBankTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create_superuser('test', 'test@test.com', 'test')
        cls.account = BankAccount.objects.create(name="Account1")
        cls.trademark = Trademark.objects.create(name="TM")
        cls.shop = Shop.objects.create(name="Shop",
                                       trademark=cls.trademark)
        cls.cost_type = CostType.objects.create(name="Opening day balance")
        cls.cost = Cost.objects.create(name="Opening day balance",
                                       cost_type=cls.cost_type,
                                       income=True)
        cls.transaction = BankTransaction.objects.create(date=date(2020, 1, 1),
                                                         shop=cls.shop,
                                                         account=cls.account,
                                                         cost=cls.cost,
                                                         amount=1000)
        
    def test_get_view_served_response(self):
        response = self.client.get(reverse('finance:bank-edit',
                                            args=(self.transaction.id,)))
        self.assertEqual(response.resolver_match.func.__name__,
                         BankEditView.as_view().__name__)

    def test_get_status_code_and_template_with_user_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:bank-edit',
                                            args=(self.transaction.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/bank_edit_form.html')

    def test_get_status_code_without_user_login(self):
        response = self.client.get(reverse('finance:bank-edit',
                                            args=(self.transaction.id,)))
        self.assertEqual(response.status_code, 302)

    def test_get_redirect_to_login(self):
        response = self.client.get(reverse('finance:bank-edit',
                                            args=(self.transaction.id,)),
                                   follow=True)
        self.assertEqual(response.redirect_chain,
            [(f'/login/?next=/finance/bank/edit/{self.transaction.id}/', 302)])

    def test_get_valid_transaction(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:bank-edit',
                                            args=(self.transaction.id,)))
        self.assertEqual(response.context['object'].shop.name, self.shop.name)
        self.assertEqual(response.context['object'].date, date(2020, 1, 1))
        self.assertEqual(response.context['object'].account.name,
                         self.account.name)
        self.assertEqual(response.context['object'].cost.name, self.cost.name)
        self.assertEqual(response.context['object'].amount, 1000)

    def test_get_invalid_transaction(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:bank-edit',
                                            args=(self.transaction.id+1,)))
        self.assertEqual(response.status_code, 404)

    def test_post_valid_data(self):
        self.client.force_login(self.user)
        response_view = self.client.get(reverse('finance:bank-view',
                                                args=(2020, 1, 1)))
        amount = response_view.context['data'][0]['transactions'][0].amount
        self.assertEqual(amount, 1000)
        response_edit = self.client.post(reverse('finance:bank-edit',
                                                 args=(self.transaction.id,)),
                                    {'date': date(2020, 1, 1),
                                     'account': self.account.id,
                                     'shop': self.shop.id,
                                     'cost': self.cost.id,
                                     'amount': 900})
        self.assertEqual(response_edit.status_code, 302)
        self.assertEqual(response_edit.url,
                         f'/finance/bank/2020/1/1/')
        response_view = self.client.get(reverse('finance:bank-view',
                                                args=(2020, 1, 1)))
        amount = response_view.context['data'][0]['transactions'][0].amount
        self.assertEqual(amount, 900)

    def test_post_invalid_account(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:bank-edit',
                                            args=(self.transaction.id,)),
                                    {'date': date(2020, 1, 1),
                                     'account': self.account.id+1,
                                     'shop': self.shop.id,
                                     'cost': self.cost.id,
                                     'amount': 1000})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/bank_edit_form.html')

    def test_post_invalid_cost(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:bank-edit',
                                            args=(self.transaction.id,)),
                                    {'date': date(2020, 1, 1),
                                     'account': self.account.id,
                                     'shop': self.shop.id,
                                     'cost': self.cost.id+1,
                                     'amount': 1000})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/bank_edit_form.html')

    def test_post_invalid_amount(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('finance:bank-edit',
                                            args=(self.transaction.id,)),
                                    {'date': date(2020, 1, 1),
                                     'account': self.account.id,
                                     'shop': self.shop.id,
                                     'cost': self.cost,
                                     'amount': 'aaa'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/bank_edit_form.html')


class DeleteBankTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create_superuser('test', 'test@test.com', 'test')
        cls.account = BankAccount.objects.create(name="Account1")
        cls.trademark = Trademark.objects.create(name="TM")
        cls.shop = Shop.objects.create(name="Shop",
                                       trademark=cls.trademark)
        cls.cost_type = CostType.objects.create(name="Opening day balance")
        cls.cost = Cost.objects.create(name="Opening day balance",
                                       cost_type=cls.cost_type,
                                       income=True)
        cls.transaction = BankTransaction.objects.create(date=date(2020, 1, 1),
                                                         shop=cls.shop,
                                                         account=cls.account,
                                                         cost=cls.cost,
                                                         amount=1000)
        
    def test_get_view_served_response(self):
        response = self.client.get(reverse('finance:bank-delete',
                                            args=(self.transaction.id,)))
        self.assertEqual(response.resolver_match.func.__name__,
                         BankDeleteView.as_view().__name__)

    def test_get_status_code_and_template_with_user_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:bank-delete',
                                            args=(self.transaction.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'finance/bank_delete_form.html')

    def test_get_status_code_without_user_login(self):
        response = self.client.get(reverse('finance:bank-delete',
                                            args=(self.transaction.id,)))
        self.assertEqual(response.status_code, 302)

    def test_get_redirect_to_login(self):
        response = self.client.get(reverse('finance:bank-delete',
                                            args=(self.transaction.id,)),
                                   follow=True)
        self.assertEqual(response.redirect_chain,
             [(f'/login/?next=/finance/bank/delete/{self.transaction.id}/',
              302)])

    def test_get_valid_shopcash(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:bank-delete',
                                            args=(self.transaction.id,)))
        self.assertEqual(response.context['object'].shop.name, self.shop.name)
        self.assertEqual(response.context['object'].date, date(2020, 1, 1))
        self.assertEqual(response.context['object'].account.name, self.account.name)
        self.assertEqual(response.context['object'].cost.name, self.cost.name)
        self.assertEqual(response.context['object'].amount, 1000)

    def test_get_invalid_shopcash(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('finance:bank-delete',
                                            args=(self.transaction.id+1,)))
        self.assertEqual(response.status_code, 404)

    def test_post_data(self):
        self.client.force_login(self.user)
        response_view = self.client.get(reverse('finance:bank-view',
                                            args=(2020, 1, 1)))
        amount = response_view.context['data'][0]['transactions'][0].amount
        self.assertEqual(amount, 1000)
        response_delete = self.client.post(reverse('finance:bank-delete',
                                               args=(self.transaction.id,)),
                                    {'date': date(2020, 1, 1),
                                     'account': self.account.id,
                                     'shop': self.shop.id,
                                     'cost': self.cost.id,
                                     'amount': 1000})
        self.assertEqual(response_delete.status_code, 302)
        self.assertEqual(response_delete.url, '/finance/bank/2020/1/1/')
        response_view = self.client.get(reverse('finance:bank-view',
                                            args=(2020, 1, 1)))
        data = response_view.context['data'][0]['transactions']
        self.assertEqual(len(data), 0)
