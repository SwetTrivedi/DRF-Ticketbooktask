# serializers.py
from rest_framework import serializers
from .models import User,Ticket,Train
from django.utils import timezone
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_owner']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_owner=validated_data.get('is_owner', False)
        )
        return user



class TicketSerializer(serializers.ModelSerializer):
    age=serializers.IntegerField(min_value=5,max_value=90)
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['user', 'id','seat_number', 'status','pnr_number']
        def validate(self, attrs):
            origin = attrs.get('origin')
            if origin:
                now = timezone.now()
                departure_time = origin.departuretimedate

                if (departure_time - now).total_seconds() < 18000:
                    raise serializers.ValidationError("You cannot book a ticket within 5 hours of train departure.")
            return attrs

class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields='__all__'