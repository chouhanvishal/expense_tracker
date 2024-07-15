from django.urls import path
from .views import ExpenseView, MyExpenseListView, FriendExpenseListView
urlpatterns = [
    path('', ExpenseView.as_view(), name='expenses'),
    path('my-expenses/', MyExpenseListView.as_view(), name='my-expense-list'),
    path('friends/', FriendExpenseListView.as_view(), name='friend-expense-list')
]
