from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Train, Booking
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)   # Set up a logger
User = get_user_model()  # Get the current custom user model


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):   # When a new user is created
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                is_normal_user=True
            )
            return user
        except Exception as e:
            logger.error(f"Error while creating user: {e}")
            raise serializers.ValidationError("Something went wrong during user creation.")


class NormalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = '__all__'

    def validate(self, data):    # Check for custom validations
        try:
            source = data.get('source_station', '').strip().lower()  # Get and clean source station
            dest = data.get('destination_station', '').strip().lower() # Get and clean destination station

            if source == dest:
                raise serializers.ValidationError("Source and destination stations cannot be the same.")

            if data.get('start_time') == data.get('end_time'):
                raise serializers.ValidationError("Start time and end time cannot be the same.")

            if data.get('arrival_date') < data.get('departure_date'):
                raise serializers.ValidationError("Arrival date cannot be before departure date.")

            if data.get('arrival_date') == data.get('departure_date'):
                raise serializers.ValidationError("Arrival date and departure date cannot be the same.")

            if not isinstance(data.get('seat_classes'), list):
                raise serializers.ValidationError("Seat classes must be a list.")

            return data
        except Exception as e:
            logger.error(f"Validation error in TrainSerializer: {e}")
            raise serializers.ValidationError("Invalid train data.")


class BookingSerializer(serializers.ModelSerializer):
    train_number = serializers.CharField(write_only=True)
    fare = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    # pnr = serializers.CharField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'train_number','passenger_name', 'passenger_age', 'passenger_gender',
            'seat_class', 'booking_type', 'boarding_station', 'destination_station',
            'fare', 'pnr', 'status', 'seat_number'
        ]
        read_only_fields = ['fare','status','seat_number']   # These fields are set automatically

    def validate(self, attrs):   
        # Get all required fields from input
        try:
            train_number = attrs.get('train_number')
            seat_class = attrs.get('seat_class')
            booking_type = attrs.get('booking_type')
            boarding_station = attrs.get('boarding_station')
            destination_station = attrs.get('destination_station')

            train = Train.objects.get(train_number=train_number)

            fare = train.get_fare(seat_class, booking_type, boarding_station, destination_station)
            if fare is None:
                raise serializers.ValidationError("Invalid seat class or booking type.")

            attrs['train'] = train
            attrs['fare'] = Decimal(str(fare)).quantize(Decimal('0.01'))
            return attrs

        except Train.DoesNotExist:
            logger.warning(f"Train not found with number: {attrs.get('train_number')}")
            raise serializers.ValidationError(f"Train with number {attrs.get('train_number')} not found.")
        except Exception as e:
            logger.error(f"Validation error in BookingSerializer: {e}")
            raise serializers.ValidationError("Error validating booking.")

    def create(self, validated_data):  #This runs when a new booking is made
        try:
            validated_data.pop('train_number', None)
            train = validated_data['train']
            seat_class = validated_data['seat_class'].lower()
            existing_seat_count = Booking.objects.filter(train=train, seat_class=seat_class).count() + 1

            if seat_class == "sleeper":
                if train.available_seats_sleeper <= 0:
                    raise serializers.ValidationError("No available Sleeper seats.")
                train.available_seats_sleeper -= 1
                seat_number = f"S{existing_seat_count}"
            elif seat_class == "ac1":
                if train.available_seats_ac1 <= 0:
                    raise serializers.ValidationError("No available AC1 seats.")
                train.available_seats_ac1 -= 1
                seat_number = f"A1-{existing_seat_count}"
            elif seat_class == "ac2":
                if train.available_seats_ac2 <= 0:
                    raise serializers.ValidationError("No available AC2 seats.")
                train.available_seats_ac2 -= 1
                seat_number = f"A2-{existing_seat_count}"
            else:
                raise serializers.ValidationError("Invalid seat class.")

            train.save()
            validated_data['seat_number'] = seat_number
            pnr = self.initial_data.get("pnr")
            if pnr:
                validated_data["pnr"]=pnr
            return Booking.objects.create(**validated_data)

        except serializers.ValidationError as ve:
            raise ve  # let DRF handle it cleanly
        except Exception as e:
            logger.error(f"Booking creation error: {e}")
            raise serializers.ValidationError("Failed to create booking due to server error.")
