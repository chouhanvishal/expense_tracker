from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Invitation
from django.contrib.auth import authenticate

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class InvitationSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    user_email = serializers.EmailField(write_only=True)
    to_user = UserSerializer(read_only=True)

    class Meta:
        model = Invitation
        fields = ['id', 'from_user', 'to_user', 'user_email', 'is_accepted', 'timestamp']

    def create(self, validated_data):
        from_user = self.context['request'].user
        user_email = validated_data['user_email']

        try:
            to_user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")

        if from_user == to_user:
            raise serializers.ValidationError("You cannot send the request to yourself")

        if Invitation.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise serializers.ValidationError("Invitation already sent to this user.")

        if from_user.friends.filter(id=to_user.id).exists():
            raise serializers.ValidationError("User is already in your friends list.")
        
        if Invitation.objects.filter(from_user=to_user, to_user=from_user).exists():
            raise serializers.ValidationError("You already received an invitation from this user.")

        # Create the invitation
        invitation = Invitation.objects.create(from_user=from_user, to_user=to_user)
        return invitation

    def update(self, instance, validated_data):
        if self.context['request'].user == instance.to_user:
            instance.is_accepted = validated_data.get('is_accepted', instance.is_accepted)
            instance.save()
            if instance.is_accepted:
                instance.from_user.friends.add(instance.to_user)
                instance.to_user.friends.add(instance.from_user)
            return instance
        else:
            raise serializers.ValidationError("You are not authorized to update this invitation.")

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        attrs['user'] = user
        return attrs

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
