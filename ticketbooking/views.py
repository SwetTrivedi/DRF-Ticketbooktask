from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from .models import User
from .permission import IsOwnerOnlyCanViewUsers,IsAdminUser
from rest_framework.permissions import IsAuthenticated
from .serializers import TicketSerializer
from .models import Ticket,Train

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_type = "Owner" if user.is_owner else "Common User"
            return Response({
                "message": "User created successfully",
                "user_type": user_type
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOnlyCanViewUsers]

    def get(self, request):
        users = User.objects.all()
        serializer = RegisterSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



class BookTicketView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if request.user.is_owner:
            return Response({"error": "Only normal users can book tickets."}, status=status.HTTP_403_FORBIDDEN)

        total_seats = 10
        booked_seats = Ticket.objects.filter(status='booked').count()

        if booked_seats < total_seats:
            assigned_seats = Ticket.objects.filter(status='booked').values_list('seat_number', flat=True)
            for i in range(1, total_seats + 1):
                seat_num = str(i)
                if seat_num not in assigned_seats:
                    seat_number = seat_num
                    break
            status_value = 'booked'
        else:
            seat_number = None
            status_value = 'waiting'

        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, seat_number=seat_number, status=status_value)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

import logging

logger = logging.getLogger(__name__)

class CancelTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pnr_number):
        try:
            ticket = Ticket.objects.get(pnr_number=pnr_number, user=request.user)
            if ticket.status=='cancelled':
                logger.info(f"User {request.user.username} tried to cancel an already canceled ticket (ID: {pnr_number})")
                return Response({'message': 'Ticket already canceled.'}, status=status.HTTP_400_BAD_REQUEST)

            ticket.status = 'cancelled'
            ticket.save()
            logger.info(f"User {request.user.username} canceled ticket (ID: {pnr_number}) successfully.")
            return Response({'message': 'Ticket canceled successfully.'}, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            logger.warning(f"User {request.user.username} tried to cancel a non-existent or unauthorized ticket (ID: {pnr_number})")

            return Response({'error': 'Ticket not found or unauthorized.'}, status=status.HTTP_404_NOT_FOUND)




class TicketStatusView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request,pnr_number):
        if not pnr_number:
            return Response({'error': 'PNR number is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            ticket = Ticket.objects.get(pnr_number=pnr_number)
            return Response({
                'event_name': ticket.event_name,
                'seat_number': ticket.seat_number,
                'booked_at': ticket.booked_at,
                'status':ticket.status
            })
        except Ticket.DoesNotExist:
            return Response({'error': 'Ticket not found '}, status=status.HTTP_404_NOT_FOUND)

class TrainCreateView(APIView):
    # permission_classes=[IsAdminUser]
    def post(self, request):
        data = request.data
        # total_seats = int(data.get('total_seats'))
        train = Train.objects.create(
            train_name=data['train_name'],
            train_number=data['train_number'],
            source=data['source'],
            destination=data['destination'],
            arrivaldatetime=data['arrivaldatetime'],
            departuretimedate=data['departuretimedate'],
            runs_daily=data.get('runs_daily', False),
            available_dates=data.get('available_dates', []) 
        )
        return Response({'message': 'Train and seats created successfully.'}, status=status.HTTP_201_CREATED)
    

from .serializers import TrainSerializer

class TrainSearchAPIView(APIView):
    def get(self, request):
        source = request.GET.get('source')
        train_name = request.GET.get('train_name')
        train_number = request.GET.get('train_number')
        destination = request.GET.get('destination')

        if not (train_name or train_number or (source and destination)):
            return Response(
                {"error": "Please provide either train_name/train_number OR both source and destination."},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = Train.objects.all()

        if train_name:
            queryset = queryset.filter(train_name__icontains=train_name)

        if train_number:
            queryset = queryset.filter(train_number=train_number)

        if source and destination:
            queryset = queryset.filter(
                source__icontains=source,
                destination__icontains=destination
            )

        serializer = TrainSerializer(queryset, many=True)
        return Response(serializer.data)
