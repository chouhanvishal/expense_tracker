from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    friends = models.ManyToManyField('self', symmetrical=False, related_name='friend_of', blank=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'
        swappable = 'AUTH_USER_MODEL'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Invitation(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_invitations', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_invitations', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invitation from {self.from_user} to {self.to_user}"

    class Meta:
        verbose_name = 'Invitation'
        verbose_name_plural = 'Invitations'
