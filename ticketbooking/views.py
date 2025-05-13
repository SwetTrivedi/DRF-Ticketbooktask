from django.shortcuts import render
from .serializers import UserSerializer,NormalUserSerializer,BookingSerializer,TrainSerializer
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Booking,Train
from .models import generate_pnr
from rest_framework import viewsets
from .permission import IsNormalUser


User = get_user_model()
class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# this class is only get normal users
class NormalUsersListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.filter(is_normal_user=True)
        serializer = NormalUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()  
    serializer_class = TrainSerializer  
    permission_classes=[IsAdminUser]


class BookTicketView(APIView):
    permission_classes = [IsNormalUser, IsAuthenticated]

    def post(self, request):
        train_number = request.data.get("train_number")
        booking_type = request.data.get("booking_type")
        seat_class = request.data.get("seat_class")
        boarding_station = request.data.get("boarding_station")
        destination_station = request.data.get("destination_station")
        pnr = generate_pnr()
        created_bookings = []

        passengers = request.data.get("passengers")

        if passengers:
            # Group booking
            for passenger in passengers:
                passenger_data = {
                    "train_number": train_number,
                    "booking_type": booking_type,
                    "seat_class": seat_class,
                    "boarding_station": boarding_station,
                    "destination_station": destination_station,
                    "passenger_name": passenger.get("name"),
                    "passenger_age": passenger.get("age"),
                    "passenger_gender": passenger.get("gender"),
                    "pnr": pnr,
                }

                serializer = BookingSerializer(data=passenger_data)
                if serializer.is_valid():
                    serializer.save()
                    created_bookings.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            # Single booking
            passenger_name = request.data.get("passenger_name")
            passenger_age = request.data.get("passenger_age")
            passenger_gender = request.data.get("passenger_gender")

            if not (passenger_name and passenger_age and passenger_gender):
                return Response({"error": "Passenger details are required for single booking."}, status=status.HTTP_400_BAD_REQUEST)

            passenger_data = {
                "train_number": train_number,
                "booking_type": booking_type,
                "seat_class": seat_class,
                "boarding_station": boarding_station,
                "destination_station": destination_station,
                "passenger_name": passenger_name,
                "passenger_age": passenger_age,
                "passenger_gender": passenger_gender,
                "pnr": pnr,
            }

            serializer = BookingSerializer(data=passenger_data)
            if serializer.is_valid():
                serializer.save()
                created_bookings.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"pnr": pnr, "bookings": created_bookings}, status=status.HTTP_201_CREATED)