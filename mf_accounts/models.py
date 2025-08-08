# mf_accounts/models.py

from django.db import models

class AccountChart(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True, null=True)
    type = models.CharField(max_length=20, choices=[
        ('Asset', 'Asset'),
        ('Liability', 'Liability'),
        ('Income', 'Income'),
        ('Expense', 'Expense')
    ])
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'account_chart'

    def __str__(self):
        return f"{self.code} - {self.name}"


class JournalEntry(models.Model):
    entry_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    reference = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'journal_entry'

    def __str__(self):
        return f"Entry {self.id} - {self.entry_date}"


class JournalLine(models.Model):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE)
    account = models.ForeignKey(AccountChart, on_delete=models.PROTECT)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    memo = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'journal_line'


class IncomeRecord(models.Model):
    source = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date_received = models.DateField()
    description = models.TextField(blank=True, null=True)
    document_path = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'income_record'


class ExpenseRecord(models.Model):
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date_paid = models.DateField()
    description = models.TextField(blank=True, null=True)
    paid_by = models.IntegerField()
    method = models.CharField(max_length=20, choices=[('Cash', 'Cash'), ('Bank', 'Bank')])
    document_path = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'expense_record'


class CoachCashFloat(models.Model):
    coach_id = models.IntegerField()
    issued_date = models.DateField()
    amount_issued = models.DecimalField(max_digits=15, decimal_places=2)
    amount_spent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        db_table = 'coach_cash_float'


class CoachCashTransaction(models.Model):
    coach_id = models.IntegerField()
    float = models.ForeignKey(CoachCashFloat, on_delete=models.CASCADE)
    date_paid = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    referee_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    document_path = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'coach_cash_transaction'


class AuditLog(models.Model):
    user_id = models.IntegerField()
    action = models.CharField(max_length=100)
    model_name = models.CharField(max_length=50)
    record_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_log'