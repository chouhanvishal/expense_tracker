from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from user_management.models import Invitation
from user_management.serializers import RegisterSerializer, InvitationSerializer, LoginSerializer, FriendSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.db.models import Q
import logging

logger = logging.getLogger('users')

class RegisterView(generics.CreateAPIView):
    """
    API view for registering a new user.

    Allows any user to register with provided credentials.

    Permissions:
    - AllowAny: No authentication required.

    Methods:
    - POST: Creates a new user with provided data.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """
        Creates a new user with provided serializer data.

        Args:
        - serializer (RegisterSerializer): Serializer instance containing user registration data.

        Returns:
        - Response: HTTP response indicating success or failure.
        """
        try:
            serializer.save()
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            raise

class InvitationViewSet(viewsets.ModelViewSet):
    """
    API viewset for managing user invitations.

    Allows authenticated users to retrieve, create, update, and delete invitations.

    Permissions:
    - IsAuthenticated: User must be authenticated.

    Methods:
    - GET: Retrieves invitations for the authenticated user.
    - POST: Creates a new invitation from the authenticated user.
    - PUT/PATCH: Updates an invitation (only accepted field).
    """
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves invitations for the authenticated user.

        Returns:
        - QuerySet: Invitations filtered by to_user and is_accepted=False.
        """
        try:
            user = self.request.user
            return Invitation.objects.filter((Q(to_user=user)) & Q(is_accepted=False))
        except Exception as e:
            logger.error(f"Error fetching invitations: {str(e)}")
            return Invitation.objects.none()

    def perform_create(self, serializer):
        """
        Creates a new invitation from the authenticated user.

        Args:
        - serializer (InvitationSerializer): Serializer instance containing invitation data.

        Returns:
        - Response: HTTP response indicating success or failure.
        """
        try:
            serializer.save(from_user=self.request.user)
        except Exception as e:
            logger.error(f"Error creating invitation: {str(e)}")
            raise

    def update(self, request, *args, **kwargs):
        """
        Updates an invitation's acceptance status (is_accepted).

        Args:
        - request: HTTP request object containing updated data.
        - args: Additional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - Response: HTTP response indicating success or failure.
        """
        try:
            instance = Invitation.objects.get(id=kwargs['pk'])
            if request.user == instance.to_user:
                if 'is_accepted' in request.data and request.data['is_accepted']:
                    instance.is_accepted = True
                    instance.save()
                    instance.from_user.friends.add(instance.to_user)
                    instance.to_user.friends.add(instance.from_user)
                    logger.info(f"Invitation accepted: {instance}")
                    return Response({"detail": "Invitation accepted."}, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({"detail": "Please provide 'is_accepted' value as True or False."}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({"detail": "You are not authorized to update this invitation."}, status=status.HTTP_403_FORBIDDEN)
        except Invitation.DoesNotExist:
            return Response({"detail": "Invitation does not exist"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error updating invitation: {str(e)}")
            return Response({"detail": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    """
    API view for user login using credentials.

    Allows users to authenticate and obtain JWT tokens for subsequent API requests.

    Methods:
    - POST: Validates user credentials and generates JWT tokens on successful login.
    """
    serializer_class = LoginSerializer

    def post(self, request):
        """
        Validates user credentials and generates JWT tokens on successful login.

        Args:
        - request: HTTP request object containing user login data.

        Returns:
        - Response: JSON response containing 'refresh' and 'access' tokens.
        """
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']

            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return Response({"detail": "Login failed"}, status=status.HTTP_400_BAD_REQUEST)

class FriendListView(generics.ListAPIView):
    """
    API view for retrieving a list of friends for the authenticated user.

    Retrieves the list of friends associated with the authenticated user.

    Permissions:
    - IsAuthenticated: User must be authenticated.

    Methods:
    - GET: Retrieves the list of friends for the authenticated user.
    """
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves the list of friends for the authenticated user.

        Returns:
        - QuerySet: List of friends associated with the authenticated user.
        """
        try:
            user = self.request.user
            return user.friends.all()
        except Exception as e:
            logger.error(f"Error fetching friends list: {str(e)}")
