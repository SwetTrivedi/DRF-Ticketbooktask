from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CustomUser
# Create your tests here.
# class Registertest(APITestCase):
#     def test_register(self):
#         data={
#             # "username":"jay",
#             "password":"jay",
#             "email":"jay@gmail.com",
#         }
#         response=self.client.post('/register/',data=data,format="json")
#         data1=response.json()
#         print(data1)
#         self.assertEqual(response.status_code,status.HTTP_201_CREATED)

# class LoginTest(APITestCase):
#     def setUp(self):
#         self.user = CustomUser.objects.create_user(
#             username="swet",
#             email="swet@example.com",
#             password="swet1234"
#         )

#     def test_login_success(self):
#         data = {
#             "username": "swet",
#             "password": "swet1234"
#         }

#         response = self.client.post('/login/', data, format='json')

#         self.assertEqual(response.status_code, 200)
#         self.assertIn("message", response.data)
#         print(response)
#         self.assertEqual(response.data["message"], "Login successful")

#     def test_login_invalid_password(self):
#         data = {
#             "username": "swet",
#             "password": "wrongpassword"
#         }

#         response = self.client.post('/login/', data, format='json')

#         self.assertEqual(response.status_code, 401)
#         self.assertIn("error", response.data)
#         self.assertEqual(response.data["error"], "Invalid credentials")

#     def test_login_missing_fields(self):
#         data = {
#             "username": "swet"
#             # password is missing
#         }

#         response = self.client.post('/login/', data, format='json')

#         self.assertEqual(response.status_code, 401)
#         self.assertIn("error",response.data)







# from rest_framework.test import APIClient


# class TrainViewSetTest(TestCase):
#     # def setUp(self):
#     #     self.client = APIClient()
#     #     self.admin_user = CustomUser.objects.create_user(
#     #         username='adminuser',
#     #         password='adminpass',
#     #         is_staff=True
#     #     )
#     #     self.client.force_authenticate(user=self.admin_user)
#     def test_train_create(self):
#         Headers={'Authorization':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUyNTAxMzg1LCJpYXQiOjE3NDczMTczODUsImp0aSI6IjU4MjQyODZhMjIwYTQ4YmE4OTRlZDExZDQ2ZGE3ZjcwIiwidXNlcl9pZCI6Mn0. AMdCX9ASnrGBPZhZ36WFaovjZd-jzEZLJtJZ0zxV_Uo'}
#         data = {
#                 "train_number": "12346",
#                 "train_name": "SuperFast Express",
#                 "source_station": "Delhi",
#                 "destination_station": "Mumbai",
#                 "start_time": "10:00:00",
#                 "end_time": "20:00:00",
#                 "departure_date": "2025-06-01",
#                 "arrival_date": "2025-06-02",
#                 "intermediate_stops": ["Agra", "Jaipur", "Surat"],
#                 "train_type": "Express",
#                 "seat_classes": ["Sleeper", "AC1", "AC2"],
#                 "total_seats_sleeper": 150,
#                 "total_seats_ac1": 50,
#                 "total_seats_ac2": 75,
#                 "fare_normal": {"Sleeper": 2, "AC1": 5, "AC2": 4},
#                 "fare_tatkal": {"Sleeper": 3, "AC1": 7, "AC2": 6},
#                 "total_distance": 500,
#                 "train_status": True,
#                 "duration":"12:00"
#         }
#         response = self.client.post("/api/trains/", data, headers=Headers,format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)




