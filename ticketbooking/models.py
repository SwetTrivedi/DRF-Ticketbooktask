from django.db import models

from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    is_owner = models.BooleanField(default=False)

    def __str__(self):
        return self.username



class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=100)
    seat_number = models.CharField(max_length=10)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event_name} - {self.seat_number}"
