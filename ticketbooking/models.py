from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils import timezone
class CustomUser(AbstractUser):
    is_normal_user= models.BooleanField(default=True)  

    def __str__(self):
        return self.username

import random
import string

def generate_pnr():
    return ''.join(random.choices(string.digits, k=8))

def get_current_date():
    return timezone.now().date()

class Train(models.Model):
    train_number = models.CharField(max_length=10, unique=True)
    train_name = models.CharField(max_length=100)
    source_station = models.CharField(max_length=100)
    destination_station = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    departure_date = models.DateField()  
    arrival_date = models.DateField()  
    intermediate_stops = models.JSONField(default=list)
    train_type = models.CharField(max_length=50)
    seat_classes = models.JSONField()
    total_seats_sleeper = models.IntegerField(default=0)
    total_seats_ac1 = models.IntegerField(default=0)
    total_seats_ac2 = models.IntegerField(default=0)
    available_seats_sleeper = models.IntegerField(default=0)
    available_seats_ac1 = models.IntegerField(default=0)
    available_seats_ac2 = models.IntegerField(default=0)
    fare_normal = models.JSONField(default=dict)  
    fare_tatkal = models.JSONField(default=dict)  
    total_distance = models.IntegerField()
    train_status = models.BooleanField(default=True)  
    duration = models.DurationField()

    def get_station_order(self):
        return [self.source_station] + self.intermediate_stops + [self.destination_station]

    def __str__(self):
        return f"{self.train_name} ({self.train_number})"
    
    def get_fare(self, seat_class, booking_type="Normal", boarding_station=None):
        if boarding_station is None:
            boarding_station = self.source_station
        fare_distance = self.calculate_distance(boarding_station)
        base_fare = self.get_base_fare(seat_class, booking_type)
        if base_fare is None:
            return None
        return base_fare * fare_distance

    def calculate_distance(self, boarding_station):
        if boarding_station == self.source_station:
            return self.total_distance
        elif boarding_station in self.intermediate_stops.split(','):
            return self.total_distance / 2  
        elif boarding_station == self.destination_station:
            return 0  
        else:
            raise ValueError(f"Invalid boarding station: {boarding_station}")

    def get_base_fare(self, seat_class, booking_type="Normal"):
        if booking_type == "Tatkal":
            return self.fare_tatkal.get(seat_class, None)
        return self.fare_normal.get(seat_class, None)
    
    
    def save(self, *args, **kwargs):
        if self._state.adding: 
            self.available_seats_sleeper = self.total_seats_sleeper
            self.available_seats_ac1 = self.total_seats_ac1
            self.available_seats_ac2 = self.total_seats_ac2
        super().save(*args, **kwargs)
    
class Booking(models.Model):
    BOOKING_TYPE_CHOICES = [
        ("Normal", "Normal"),
        ("Tatkal", "Tatkal")
    ]

    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="bookings")
    pnr = models.CharField(max_length=8, default=generate_pnr, editable=False)
    passenger_name = models.CharField(max_length=100)
    passenger_age = models.PositiveIntegerField()
    passenger_gender = models.CharField(max_length=10)
    seat_class = models.CharField(max_length=20)  
    booking_type = models.CharField(max_length=10, choices=BOOKING_TYPE_CHOICES)
    boarding_station = models.CharField(max_length=100)
    destination_station = models.CharField(max_length=100)
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="Confirmed")
    booking_time = models.DateTimeField(auto_now_add=True)
    seat_number = models.CharField(max_length=10, null=True, blank=True) 
    
    
    def __str__(self):
        return f"{self.passenger_name} -PNR{self.pnr}"