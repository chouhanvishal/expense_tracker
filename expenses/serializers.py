# serializers.py

from rest_framework import serializers
from .models import Expense, ExpenseParticipant
from user_management.serializers import UserSerializer
from user_management.models import User


class ExpenseParticipantSerializer(serializers.ModelSerializer):
    participant = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ExpenseParticipant
        fields = ['participant', 'paid_share', 'owes_share']

class ExpenseSerializer(serializers.ModelSerializer):
    participants = ExpenseParticipantSerializer(many=True)

    class Meta:
        model = Expense
        fields = ['amount', 'description', 'date_created', 'tax', 'participants']


    def create(self, validated_data):
        participants_data = validated_data.pop('participants')
        expense = Expense.objects.create(**validated_data)

        total_amount = expense.amount
        total_participants = len(participants_data)
        friends = self.context['request'].user.friends.all()

        for participant_data in participants_data:
            paid_share = participant_data.get('paid_share', 0)
            owes_share = total_amount / total_participants - paid_share
            participant = participant_data['participant']  # Extract the participant ID
            if participant not in friends:
                raise serializers.ValidationError(f"Participant {participant.username} is not in the list of friends")

            ExpenseParticipant.objects.create(expense=expense, participant=participant, paid_share=paid_share, owes_share=owes_share)

        return expense
