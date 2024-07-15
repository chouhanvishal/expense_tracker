from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from user_management.models import User, Invitation 

class RegisterViewTestCase(APITestCase):

    def test_register_user(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # Verify that a User object was created in the database
        user_exists = User.objects.filter(username='testuser').exists()
        self.assertTrue(user_exists)


class InvitationViewSetTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.client.force_authenticate(user=self.user)

    def test_list_invitations(self):
        invitation = Invitation.objects.create(to_user=self.user)
        url = reverse('invitation-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['to_user'], self.user.id)
        self.assertFalse(response.data[0]['is_accepted'])

    def test_accept_invitation(self):
        from_user = User.objects.create(username='from_user')
        invitation = Invitation.objects.create(from_user=from_user, to_user=self.user)

        url = reverse('invitation-detail', args=[invitation.id])
        data = {'is_accepted': True}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invitation.refresh_from_db()
        self.assertTrue(invitation.is_accepted)
        
        # Verify that friendship is established
        self.assertTrue(self.user.friends.filter(username='from_user').exists())


class LoginViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')

    def test_login_user(self):
        url = reverse('login')  # Assuming you have a 'login' URL name
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)