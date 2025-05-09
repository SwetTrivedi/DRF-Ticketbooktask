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
from django.urls import path, include
from ticketbooking.views import RegisterView,UserListView,BookTicketView,CancelTicketView,TicketStatusView,TrainCreateView,TrainSearchAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterView.as_view()),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/', UserListView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('bookticket/', BookTicketView.as_view()),
    path('cancelticket/<int:pnr_number>/', CancelTicketView.as_view(), name='cancel-ticket'),
    path('ticketstatus/<str:pnr_number>/', TicketStatusView.as_view(), name='ticket-status'),
    path('traincreate/', TrainCreateView.as_view(), name='traincrate'),
    path('trainsearch/', TrainSearchAPIView.as_view(), name='train-search'),

]

