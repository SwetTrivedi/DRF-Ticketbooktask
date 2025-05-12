"""
URL configuration for ticket project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ticketbooking.views import UserRegistrationView, UserListView, BookTicketView, CancelTicketView, TicketStatusView, SearchTrainView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserListView.as_view(), name='user-view'),
    path('book/', BookTicketView.as_view()),
    path('cancel/<int:pnr_number>/', CancelTicketView.as_view(), name='cancel-ticket'),
    path('ticketstatus/<str:pnr_number>/', TicketStatusView.as_view(), name='ticket-status'),
    path('trainsearch/', SearchTrainView.as_view(), name='search-trains'),
]

