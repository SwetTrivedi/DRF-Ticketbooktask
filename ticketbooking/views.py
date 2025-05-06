from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from .models import User
from .permission import IsOwnerOnlyCanViewUsers
from rest_framework.permissions import IsAuthenticated
from .serializers import TicketSerializer
from .models import Ticket

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
        
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Ticket booked successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
