from rest_framework import status
from rest_framework.response import Response
from datetime import date
from django.shortcuts import get_object_or_404
from .models import Ticket, CustomUser, Train, generate_pnr
from rest_framework.views import APIView
from .serializers import UserSerializer, TicketSerializer, TrainSerializer
from rest_framework.permissions import IsAuthenticated
from .permission import IsOwnerOnlyCanViewUsers
import logging

logger = logging.getLogger(__name__)


class UserRegistrationView(APIView):
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Error in user registration")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOnlyCanViewUsers]

    def get(self, request):
        try:
            users = CustomUser.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Error fetching user list")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            if request.user.is_owner:
                return Response({"error": "Only normal users can book tickets."}, status=status.HTTP_403_FORBIDDEN)

            train_number = request.data.get('train_number')
            departure_date = request.data.get('departure_date')
            seat_class = request.data.get('seat_class')
            number_of_seats = request.data.get('number_of_seats')
            passengers = request.data.get('passengers', [])

            if not all([train_number, departure_date, seat_class, number_of_seats]):
                return Response({"error": "Train number, departure date, seat class and number of seats are required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                number_of_seats = int(number_of_seats)
                if number_of_seats <= 0 or number_of_seats > 6:
                    return Response({"error": "You can book between 1 to 6 seats only."}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({"error": "Number of seats must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

            if len(passengers) != number_of_seats:
                return Response({"error": "Please provide name and age for each passenger."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                departure_date_obj = date.fromisoformat(departure_date)
                if departure_date_obj < date.today():
                    return Response({"error": "You cannot book tickets for a past date."}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({"error": "Invalid departure date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                train = Train.objects.get(train_number=train_number, departure_date=departure_date)
            except Train.DoesNotExist:
                return Response({"error": "Train not found for the given date."}, status=status.HTTP_404_NOT_FOUND)

            if seat_class not in train.seat_info_array:
                return Response({"error": f"{seat_class} is not available for this train."}, status=status.HTTP_400_BAD_REQUEST)

            booked_tickets = Ticket.objects.filter(
                train_number=train_number,
                departure_date=departure_date,
                seat_class=seat_class,
                status='booked'
            )
            assigned_seats = set(booked_tickets.values_list('seat_number', flat=True))
            available_count = train.available_seats or 0

            booked_seats_list = []
            next_seat = 1

            while len(booked_seats_list) < min(available_count, number_of_seats):
                seat_label = f"{seat_class}-{next_seat}"
                if seat_label not in assigned_seats:
                    booked_seats_list.append(seat_label)
                next_seat += 1

            while len(booked_seats_list) < number_of_seats:
                booked_seats_list.append(None)

            group_pnr = generate_pnr()

            created_tickets = []
            for i, seat in enumerate(booked_seats_list):
                passenger_info = passengers[i]
                name = passenger_info.get('name')
                age = passenger_info.get('age')

                if not name or age is None:
                    return Response({"error": "Each passenger must have a name and age."}, status=status.HTTP_400_BAD_REQUEST)

                ticket_status = 'booked' if seat else 'waiting'

                ticket_data = {
                    'user': request.user.id,
                    'train_number': train_number,
                    'departure_date': departure_date,
                    'seat_class': seat_class,
                    'seat_number': seat,
                    'status': ticket_status,
                    'event_name': f"Train {train_number} Ride",
                    'source': train.source,
                    'destination': train.destination,
                    'number_of_seats': 1,
                    'age': age,
                    'name': name,
                    'pnr_number': group_pnr
                }

                serializer = TicketSerializer(data=ticket_data)
                if serializer.is_valid():
                    serializer.save(user=request.user)
                    created_tickets.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            booked_count = sum(1 for seat in booked_seats_list if seat)
            train.booked_seats = (train.booked_seats or 0) + booked_count
            train.available_seats = (train.available_seats or train.total_seats) - number_of_seats
            train.save()

            return Response({
                "message": f"{len(created_tickets)} ticket(s) created: {booked_count} booked, {number_of_seats - booked_count} waiting.",
                "pnr": group_pnr,
                "tickets": created_tickets
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("Error booking ticket")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pnr_number):
        try:
            ticket = get_object_or_404(Ticket, pnr_number=pnr_number, user=request.user)

            if ticket.status == 'cancelled':
                return Response({'message': 'Ticket already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                train = Train.objects.get(train_number=ticket.train_number, departure_date=ticket.departure_date)
            except Train.DoesNotExist:
                return Response({'error': 'Associated train not found.'}, status=status.HTTP_404_NOT_FOUND)

            if ticket.status == 'booked':
                seat_freed = ticket.seat_number
                ticket.status = 'cancelled'
                ticket.seat_number = None
                ticket.save()

                train.booked_seats = max((train.booked_seats or 0) - 1, 0)

                waiting_ticket = Ticket.objects.filter(
                    train_number=ticket.train_number,
                    departure_date=ticket.departure_date,
                    seat_class=ticket.seat_class,
                    status='waiting'
                ).order_by('booked_at').first()

                if waiting_ticket:
                    waiting_ticket.status = 'booked'
                    waiting_ticket.seat_number = seat_freed
                    waiting_ticket.save()
                else:
                    train.available_seats = (train.available_seats or 0) + 1

                train.save()

            else:
                ticket.status = 'cancelled'
                ticket.save()

            return Response({'message': 'Ticket cancelled successfully.'}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Error cancelling ticket")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TicketStatusView(APIView):
    def get(self, request, pnr_number):
        try:
            ticket = Ticket.objects.get(pnr_number=pnr_number)
            serializer = TicketSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response({'error': 'Ticket not found or unauthorized.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("Error fetching ticket status")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchTrainView(APIView):
    def get(self, request):
        try:
            source = request.query_params.get('source')
            destination = request.query_params.get('destination')
            train_number = request.query_params.get('train_number')
            date = request.query_params.get('date')

            if train_number:
                trains = Train.objects.filter(train_number=train_number)
            else:
                if not all([source, destination]):
                    return Response({"error": "Please provide source and destination"}, status=400)

                if not date:
                    from datetime import date as today_date
                    date = today_date.today().isoformat()

                trains = Train.objects.filter(
                    source__iexact=source,
                    destination__iexact=destination,
                    departure_date=date
                )

            if trains.exists():
                serializer = TrainSerializer(trains, many=True)
                return Response(serializer.data)
            else:
                return Response({"error": "No trains found"}, status=404)
        except Exception as e:
            logger.exception("Error searching trains")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            if not request.user.is_staff:
                return Response({"error": "Only admin can add train"}, status=403)

            serializer = TrainSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        except Exception as e:
            logger.exception("Error adding train")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
