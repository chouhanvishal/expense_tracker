from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from expenses.models import Expense, ExpenseParticipant
from expenses.serializers import ExpenseSerializer
from django.db import models
from rest_framework.response import Response
from user_management.models import User
import logging

logger = logging.getLogger('expenses')

class ExpenseView(generics.ListCreateAPIView):
    """
    API view for listing and creating expenses.

    Retrieves expenses created by the authenticated user.
    Allows authenticated users to create new expenses.

    Permissions:
    - User must be authenticated.

    Methods:
    - GET: Retrieves expenses created by the authenticated user.
    - POST: Creates a new expense associated with the authenticated user.
    """
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves expenses created by the authenticated user.

        Returns:
        - QuerySet: Expenses created by the authenticated user.
        """
        try:
            user = self.request.user
            return Expense.objects.filter(created_by=user)
        except Exception as e:
            logger.error(f"Error fetching expenses: {str(e)}")
            return Expense.objects.none()

    def perform_create(self, serializer):
        """
        Creates a new expense associated with the authenticated user.

        Args:
        - serializer (ExpenseSerializer): Serializer instance containing expense data.

        Returns:
        - Response: HTTP response indicating success or failure.
        """
        try:
            serializer.save(created_by=self.request.user)
        except Exception as e:
            logger.error(f"Error creating expense: {str(e)}")

class MyExpenseListView(generics.GenericAPIView):
    """
    API view for listing expenses and balance details for the authenticated user.

    Retrieves expenses where the authenticated user is either the creator or a participant.
    Calculates total balance and amounts owed for the authenticated user.

    Permissions:
    - User must be authenticated.

    Methods:
    - GET: Retrieves expenses and balance details for the authenticated user.
    """
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieves expenses and balance details for the authenticated user.

        Returns:
        - Response: JSON response containing total balance, amounts owed, friends' debts, and list of expenses.
        """
        try:
            user = request.user

            expenses = Expense.objects.filter(created_by=user) | Expense.objects.filter(participants__participant=user)

            total_owed = ExpenseParticipant.objects.filter(participant=user).aggregate(total=models.Sum('owes_share'))['total'] or 0
            total_owed_to_me = ExpenseParticipant.objects.filter(expense__created_by=user).aggregate(total=models.Sum('paid_share'))['total'] or 0
            total_balance = total_owed_to_me - total_owed

            friends_owed_to_me = ExpenseParticipant.objects.filter(expense__created_by=user, owes_share__gt=0).values('participant').annotate(total=models.Sum('owes_share'))

            response_data = {
                'total_balance': total_balance,
                'total_owed': total_owed,
                'total_owed_to_me': total_owed_to_me,
                'friends_owed_to_me': friends_owed_to_me,
                'expenses': self.get_serializer(expenses, many=True).data
            }

            return Response(response_data)
        except Exception as e:
            logger.error(f"Error fetching expenses and balance details: {str(e)}")
            return Response({"error": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FriendExpenseListView(generics.ListAPIView):
    """
    API view for listing expenses of friends for the authenticated user.

    Retrieves expenses where the authenticated user's friends are participants.

    Permissions:
    - User must be authenticated.

    Methods:
    - GET: Retrieves expenses of friends for the authenticated user.
    """
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieves expenses of friends for the authenticated user.

        Returns:
        - Response: JSON response containing expenses of each friend.
        """
        try:
            user = request.user

            friends = user.friends.all()
            friends_expenses = []

            for friend in friends:
                expenses = Expense.objects.filter(participants__participant=friend)
                serializer = self.get_serializer(expenses, many=True)
                friends_expenses.append({
                    "friend": friend.username,
                    "expenses": serializer.data
                })

            return Response(friends_expenses, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching friends' expenses: {str(e)}")
            return Response({"error": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
