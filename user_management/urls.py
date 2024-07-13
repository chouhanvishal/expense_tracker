# user/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, InvitationViewSet, LoginView, FriendListView

router = DefaultRouter()
router.register(r'invitations', InvitationViewSet, basename='invitation')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('friends/', FriendListView.as_view(), name='friends-list'),
    path('', include(router.urls)),
]
