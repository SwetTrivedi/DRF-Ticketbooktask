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

# ----------------------- Admin and User Can Register here -----------------------
class RegisterUserView(APIView):
    try:
        def post(self, request):
                try:
                    serializer = UserSerializer(data=request.data)
                    if serializer.is_valid():
                        serializer.save()  # after registration save the data in database 
                        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    logger.error(f"Error in RegisterUserView POST: {e}")
                    return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Error while defining RegisterUserView: {e}")

# ----------------------- Admin Can see the All users Data -----------------------
try:
    class NormalUsersListView(APIView):
        permission_classes = [IsAdminUser] # Check the Authentication of admin 

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

# ----------------------- Admin Can Perform The CRUD Opertaion like add the train and etc . -----------------------
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

# -----------------------User Can Book the ticket -----------------------
try:
    class BookTicketView(APIView): 
        permission_classes = [IsNormalUser, IsAuthenticated]   # Check the user is authenticated or not (user=Normaluser not Superuser )

        def post(self, request):
            try:
                train_number = request.data.get("train_number")  #pass the train number
                booking_type = request.data.get("booking_type")  #pass the booking_type(type=Tatkal ,Normal )
                seat_class = request.data.get("seat_class")      #Pass the seat class (seat_class= 1AC,2AC,Sleeper)
                boarding_station = request.data.get("boarding_station")          # pass the Boarding_station Like delhi , kanpur etc
                destination_station = request.data.get("destination_station")    # pass the destination_station like Lucknow , Banaras
                created_bookings = []     # create a empty list to append to all response at a time of ticketbooking 

                passengers = request.data.get("passengers")  # Each passenger's data will be processed individually 

                if passengers:  # This allows handling multiple passengers in a single booking 
                    group_pnr= generate_pnr() # call the Function which is define in model.py file to genrate the unique 8 digits number
                    for passenger in passengers: # Loop through each passenger in the passengers list  
                        #  Group Booking
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
                                "pnr": group_pnr,
                            }

                            serializer = BookingSerializer(data=passenger_data)
                            if serializer.is_valid():
                                serializer.save()  # Save the ticket after check the validation 
                                created_bookings.append(serializer.data)  # append the serialized data in created bookings list 
                            else:
                                logger.error(f"Validation error in group booking: {serializer.errors}")
                                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        except Exception as e:
                            logger.error(f"Error in group passenger booking: {e}")
                            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    return Response({"pnr": group_pnr, "bookings": created_bookings}, status=status.HTTP_201_CREATED)
                else:
                    # Single Booking 
                    try:
                        passenger_name = request.data.get("passenger_name")
                        passenger_age = request.data.get("passenger_age")
                        passenger_gender = request.data.get("passenger_gender")

                        if not (passenger_name and passenger_age and passenger_gender): 
                            return Response({"error": "Passenger details required."}, status=status.HTTP_400_BAD_REQUEST) # Genrate the error if user not provide the name ,age and gender 
                        unique_pnr=generate_pnr()
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
                            "pnr": unique_pnr,
                        }

                        serializer = BookingSerializer(data=passenger_data)
                        if serializer.is_valid():
                            serializer.save() # Save the ticket after check the validation 
                            created_bookings.append(serializer.data) # append the serialized data in created bookings list 
                            return Response({ "bookings": created_bookings}, status=status.HTTP_201_CREATED)
                        else:
                            logger.error(f"Validation error in single booking: {serializer.errors}")
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        # else:
                        #     logger.error(f"Validation error in single booking: {serializer.errors}")
                        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        logger.error(f"Error in single passenger booking: {e}")
                        return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


            except Exception as e:
                logger.error(f"Error in BookTicketView POST: {e}")
                return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
except Exception as e:
    logger.error(f"Error while defining BookTicketView: {e}")



from django.db.models import Q, F, Sum, Count
# -----------------------------This API returns different types of booking and train queries -------------------------
class QueryAPIView(APIView):
    def get(self, request):
        data = {
            "first and last":{
                "first_booking":BookingSerializer(Booking.objects.order_by('booking_time').first()).data,      # Get the first booking based on booking time
                "last_train":TrainSerializer(Train.objects.order_by('-departure_date').last()).data,           # Get the last train 
            },
            "Filtering": {
                "AC1_Bookings": BookingSerializer(Booking.objects.filter(seat_class='AC1'), many=True).data,     # Get all bookings where seat class is AC1
                "High_Fare_Bookings": BookingSerializer(Booking.objects.filter(fare__gt=1000), many=True).data,   # Get bookings where fare is more than 1000
            },
            "Related_Lookups": {
                "Bookings_Train_12345": BookingSerializer(Booking.objects.filter(train__train_number='12345'), many=True).data,   # Get bookings where the train number is 12345
                "Trains_With_Confirmed_Bookings": TrainSerializer(Train.objects.filter(bookings__status='Confirmed').distinct(), many=True).data,    # Get trains which have any confirmed booking
            },
            "Aggregation": {
                "Total_Fare": Booking.objects.aggregate(total_fare=Sum('fare')),    # Calculate total fare of all bookings
                "Booking_Counts_By_Class": list(Booking.objects.values('seat_class').annotate(count=Count('id'))),    # Count bookings for each seat class
            },
            "Q_and_F_Expressions": {
                "AC1_or_Tatkal": BookingSerializer(Booking.objects.filter(Q(seat_class='AC1') | Q(booking_type='Tatkal')), many=True).data,   # Get bookings where seat class is AC1 or booking type is Tatkal
                "Fare_Greater_Than_Approx": BookingSerializer(Booking.objects.filter(fare__gt=F('fare') - 100), many=True).data,   # Get bookings where fare is greater than fare - 100 (approx check)
            }
        }
        return Response(data)