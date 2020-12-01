from django.urls import path

from . import views


app_name = "staff"

urlpatterns = [
    path('index/<int:month_delta>/', views.StaffListView.as_view(), name='staff-list'),
    path('timesheet/edit/<int:pk>/', views.TimesheetEditView.as_view(), name='timesheet-edit'),
    path('timesheet/delete/<int:pk>/', views.TimesheetDeleteView.as_view(), name='timesheet-delete'),
    path('<int:pk>/<int:month_delta>/', views.ShopTimesheetView.as_view(), name='shop-timesheet'),
    path('<int:pk>/timesheet/select/', views.SelectTimesheetView.as_view(), name='select-timesheet'),
    path('<int:pk>/timesheet/<int:year>/<int:month>/<int:day>/', views.TimesheetCreateView.as_view(), name='timesheet-view'),
]
