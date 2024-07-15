from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from user_management.models import User
from expenses.models import Expense

class ExpenseViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.client.force_authenticate(user=self.user)

    def test_create_expense(self):
        url = reverse('expense-list')
        data = {
            'title': 'Test Expense',
            'amount': 100.00,
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expense = Expense.objects.get(pk=response.data['id'])
        self.assertEqual(expense.title, 'Test Expense')
        self.assertEqual(expense.amount, 100.00)
        self.assertEqual(expense.created_by, self.user)

    def test_list_expenses(self):
        Expense.objects.create(title='Expense 1', amount=50.00, created_by=self.user)
        Expense.objects.create(title='Expense 2', amount=75.00, created_by=self.user)

        url = reverse('expense-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

class MyExpenseListViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.client.force_authenticate(user=self.user)

    def test_list_my_expenses(self):
        Expense.objects.create(title='Expense 1', amount=50.00, created_by=self.user)
        Expense.objects.create(title='Expense 2', amount=75.00, created_by=self.user)

        url = reverse('my-expense-list')  # Assuming you have a 'my-expense-list' URL name

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['expenses']), 2)

        total_balance = response.data['total_balance']
        total_owed = response.data['total_owed']
        total_owed_to_me = response.data['total_owed_to_me']
        self.assertEqual(total_balance, total_owed_to_me - total_owed)
