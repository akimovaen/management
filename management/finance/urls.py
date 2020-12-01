from django.urls import path

from . import views


app_name = "finance"

urlpatterns = [
    path('no_access/', views.NoAccessView.as_view(), name='no-access'),
    path('greeting/', views.GreetingView.as_view(), name='greeting'),
    path('<int:pk>/<int:month_delta>/', views.ShopDetailView.as_view(), name='shop-detail'),
    path('shops/<int:month_delta>/', views.ShopListView.as_view(), name='shop-list'),
    path('bank/select/', views.SelectBankView.as_view(), name='select-bank'),
    path('bank/edit/<int:pk>/', views.BankEditView.as_view(), name='bank-edit'),
    path('bank/delete/<int:pk>/', views.BankDeleteView.as_view(), name='bank-delete'),
    path('bank/<int:year>/<int:month>/<int:day>/', views.BankView.as_view(), name='bank-view'),
    path('<int:pk>/report/select/', views.SelectReportView.as_view(), name='select-report'),
    path('report/edit/<int:pk>/', views.ReportEditView.as_view(), name='report-edit'),
    path('report/delete/<int:pk>/', views.ReportDeleteView.as_view(), name='report-delete'),
    path('<int:pk>/report/<int:year>/<int:month>/<int:day>/', views.ReportCreateView.as_view(), name='report-view'),
    path('<int:pk>/report/<int:year>/<int:month>/<int:day>/complete/', views.ReportCompleteView.as_view(), name='report-complete'),
]
