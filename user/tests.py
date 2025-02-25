from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.db import connections


class TicketAPITestCase(APITestCase):
    def setUp(self):
        # for conn in connections.all():
        #     try:
        #         conn.close()
        #     except:
        #         pass
        self.admin_user = get_user_model().objects.create_user(
            username="admin", password="adminpass", role="admin"
        )
        self.agent_user = get_user_model().objects.create_user(
            username="agent", password="agentpass", role="agent"
        )
        self.customer_user = get_user_model().objects.create_user(
            username="customer", password="customerpass", role="customer"
        )
        self.client.login(username="admin", password="adminpass")

    def test_register(self):
        response = self.client.post(
            "/api/user/register/",
            {
                "username": "test1",
                "email": "test1@gmail.com",
                "password": "test1",
                "role": "test1",
            },
        )
        self.assertEqual(response.status_code, 201)

    def test_obtain_jwt_token(self):
        response = self.client.post(
            "/api/user/login/", {"username": "admin", "password": "adminpass"}
        )
        self.assertEqual(response.status_code, 200)


# 1. Test Authentication
# obtain JWT token (/api/token/)
# Refresh token (/api/token/refresh/)
