from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Invitation
from .serializers import RegisterSerializer, InvitationSerializer, LoginSerializer, FriendSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Invitation.objects.filter(from_user=user) | Invitation.objects.filter(to_user=user)

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    def update(self, request, *args, **kwargs):
        import pdb
        pdb.set_trace()
        instance = self.get_object()
        if request.user == instance.to_user:
            if 'is_accepted' in request.data and request.data['is_accepted']:
                instance.is_accepted = True
                instance.save()
                instance.from_user.friends.add(instance.to_user)
                instance.to_user.friends.add(instance.from_user)
                return super().update(request, *args, **kwargs)
            else:
                return Response({"detail": "Please provide 'is_accepted' value as True or False."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"detail": "You are not authorized to update this invitation."}, status=status.HTTP_403_FORBIDDEN)

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class FriendListView(generics.ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.friends.all()
