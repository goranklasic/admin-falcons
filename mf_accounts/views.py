# mf_accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import IncomeRecord, ExpenseRecord, CoachCashTransaction
from .forms import IncomeRecordForm, ExpenseRecordForm, CoachCashTransactionForm

@login_required
def income_list(request):
    incomes = IncomeRecord.objects.all().order_by('-date_received')
    return render(request, 'mf_accounts/income_list.html', {'incomes': incomes})

@login_required
def income_create(request):
    if request.method == 'POST':
        form = IncomeRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('income_list')
    else:
        form = IncomeRecordForm()
    return render(request, 'mf_accounts/income_form.html', {'form': form})


@login_required
def expense_list(request):
    expenses = ExpenseRecord.objects.all().order_by('-date_paid')
    return render(request, 'mf_accounts/expense_list.html', {'expenses': expenses})

@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseRecordForm()
    return render(request, 'mf_accounts/expense_form.html', {'form': form})


@login_required
def coach_cash_transaction_list(request):
    transactions = CoachCashTransaction.objects.all().order_by('-date_paid')
    return render(request, 'mf_accounts/coach_cash_transaction_list.html', {'transactions': transactions})

@login_required
def coach_cash_transaction_create(request):
    if request.method == 'POST':
        form = CoachCashTransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('coach_cash_transaction_list')
    else:
        form = CoachCashTransactionForm()
    return render(request, 'mf_accounts/coach_cash_transaction_form.html', {'form': form})