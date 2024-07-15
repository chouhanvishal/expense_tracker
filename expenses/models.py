# models.py

from django.db import models
from user_management.models import User
class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_by = models.ForeignKey(User, related_name='expenses_created', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        db_table = 'expenses'
    
    def __str__(self):
        return f'Expense {self.id}: {self.description}'

class ExpenseParticipant(models.Model):
    expense = models.ForeignKey(Expense, related_name='participants', on_delete=models.CASCADE)
    participant = models.ForeignKey(User, related_name='participant_expenses', on_delete=models.CASCADE)
    paid_share = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    owes_share = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Expense Participant'
        verbose_name_plural = 'Expense Participants'
        db_table = 'expense_participants'

    def __str__(self):
        return f'Participant {self.participant.username} in Expense {self.expense.id}'
