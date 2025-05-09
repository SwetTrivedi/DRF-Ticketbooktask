from django.db import models

from django.contrib.auth.models import AbstractUser
import random
from django.utils import timezone
import string

class User(AbstractUser):
    is_owner = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Train(models.Model):
    train_name=models.CharField(max_length=255)
    train_number=models.CharField(max_length=20, unique=True)
    source=models.CharField(max_length=255)
    destination=models.CharField(max_length=255)
    arrivaldatetime=models.DateTimeField(default=timezone.now)
    departuretimedate=models.DateTimeField(default=timezone.now)
    runs_daily = models.BooleanField(default=False)
    available_dates = models.JSONField(blank=True, null=True) 
    
    def __str__(self):
        return self.train_name

def generate_pnr():
    return ''.join(random.choices(string.digits, k=8))
class Ticket(models.Model):
    STATUS_CHOICES = (
        ('booked', 'Booked'),
        ('waiting', 'Waiting'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=100)
    seat_number = models.CharField(max_length=10, null=True, blank=True)
    booked_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='booked')
    age= models.IntegerField(null=True,blank=True)
    booking_time = models.DateTimeField(default=timezone.now)
    origin = models.ForeignKey(Train,on_delete=models.CASCADE,related_name='tickets_origin')
    destinate = models.ForeignKey(Train,on_delete=models.CASCADE,related_name='tickets_destination')
    pnr_number = models.CharField(max_length=8, unique=True, default=generate_pnr)
    # total_seat=models.

    def __str__(self):
        return f"PNR: {self.pnr_number} | Seat: {self.seat_number or 'Waiting'} | Status:{self.status}"