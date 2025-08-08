# mf_accounts/forms.py

from django import forms
from .models import IncomeRecord, ExpenseRecord, CoachCashTransaction

class IncomeRecordForm(forms.ModelForm):
    class Meta:
        model = IncomeRecord
        fields = ['source', 'amount', 'date_received', 'description', 'document_path']


class ExpenseRecordForm(forms.ModelForm):
    class Meta:
        model = ExpenseRecord
        fields = ['category', 'amount', 'date_paid', 'description', 'paid_by', 'method', 'document_path']


class CoachCashTransactionForm(forms.ModelForm):
    class Meta:
        model = CoachCashTransaction
        fields = ['coach_id', 'float', 'date_paid', 'amount', 'referee_name', 'description', 'document_path']