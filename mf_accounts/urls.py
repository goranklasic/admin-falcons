# mf_accounts/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('income/', views.income_list, name='income_list'),
    path('income/new/', views.income_create, name='income_create'),
    path('expense/', views.expense_list, name='expense_list'),
    path('expense/new/', views.expense_create, name='expense_create'),
    path('coach-cash/', views.coach_cash_transaction_list, name='coach_cash_transaction_list'),
    path('coach-cash/new/', views.coach_cash_transaction_create, name='coach_cash_transaction_create'),
]