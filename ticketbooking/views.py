import logging
from django.shortcuts import render
from .serializers import UserSerializer, NormalUserSerializer, BookingSerializer, TrainSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Booking, Train
from .models import generate_pnr
from rest_framework import viewsets
from .permission import IsNormalUser

# Setup logging
logger = logging.getLogger(__name__)

User = get_user_model()

# ----------------------- RegisterUserView -----------------------
class RegisterUserView(APIView):
    try:
        def post(self, request):
                try:
                    serializer = UserSerializer(data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    logger.error(f"Error in RegisterUserView POST: {e}")
                    return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error while defining RegisterUserView: {e}")

# ----------------------- NormalUsersListView -----------------------
try:
    class NormalUsersListView(APIView):
        permission_classes = [IsAdminUser]

        def get(self, request):
            try:
                users = User.objects.filter(is_normal_user=True)
                serializer = NormalUserSerializer(users, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error in NormalUsersListView GET: {e}")
                return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
except Exception as e:
    logger.error(f"Error while defining NormalUsersListView: {e}")

# ----------------------- TrainViewSet -----------------------
try:
    class TrainViewSet(viewsets.ModelViewSet):
        queryset = Train.objects.all()
        serializer_class = TrainSerializer
        permission_classes = [IsAdminUser]

        def list(self, request, *args, **kwargs):
            try:
                return super().list(request, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error in TrainViewSet LIST: {e}")
                return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
except Exception as e:
    logger.error(f"Error while defining TrainViewSet: {e}")

# ----------------------- BookTicketView -----------------------
try:
    class BookTicketView(APIView):
        permission_classes = [IsNormalUser, IsAuthenticated]

        def post(self, request):
            try:
                train_number = request.data.get("train_number")
                booking_type = request.data.get("booking_type")
                seat_class = request.data.get("seat_class")
                boarding_station = request.data.get("boarding_station")
                destination_station = request.data.get("destination_station")
                pnr = generate_pnr()
                created_bookings = []

                passengers = request.data.get("passengers")

                if passengers:
                    for passenger in passengers:
                        try:
                            passenger_data = {
                                # "train_name":train.train_name,
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
                                logger.error(f"Validation error in group booking: {serializer.errors}")
                                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        except Exception as e:
                            logger.error(f"Error in group passenger booking: {e}")
                            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    try:
                        passenger_name = request.data.get("passenger_name")
                        passenger_age = request.data.get("passenger_age")
                        passenger_gender = request.data.get("passenger_gender")

                        if not (passenger_name and passenger_age and passenger_gender):
                            return Response({"error": "Passenger details required."}, status=status.HTTP_400_BAD_REQUEST)

                        passenger_data = {
                            # "train_name":train.train_name,
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
                            logger.error(f"Validation error in single booking: {serializer.errors}")
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        logger.error(f"Error in single passenger booking: {e}")
                        return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                return Response({"pnr": pnr, "bookings": created_bookings}, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"Error in BookTicketView POST: {e}")
                return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
except Exception as e:
    logger.error(f"Error while defining BookTicketView: {e}")
