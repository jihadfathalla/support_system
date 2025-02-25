import json
from rest_framework import status
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from support_tickets.models import Ticket


class APITestCase(TransactionTestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_user(
            username="admin", password="adminpass", role="admin"
        )

        self.agent_user = get_user_model().objects.create_user(
            username="agent", password="agentpass", role="agent"
        )
        self.client.login(username="admin", password="adminpass")

    ## ---------------- TEST TICKETS ---------------- ##
    def test_list_tickets_authenticated(self):
        """Authenticated user can list tickets"""
        self.client.logout()
        self.client.login(username="admin", password="adminpass")
        response = self.client.get("/api/tickets/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)

    def test_retrieve_ticket(self):
        """get ticket by id"""
        self.client.logout()
        self.client.login(username="admin", password="adminpass")
        ticket = Ticket.objects.create(title="Update Test", description="Update this")
        response = self.client.get(f"/api/tickets/{ticket.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_ticket_invalid_id(self):
        """Retrieving a non-existent ticket should return 400 error"""
        self.client.logout()
        self.client.login(username="admin", password="adminpass")
        invalid_url = "/api/tickets/999999/"
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_ticket(self):
        """Admin authenticated allowed to create tickets"""
        self.client.logout()
        self.client.login(username="admin", password="adminpass")
        response = self.client.post(
            "/api/tickets/", {"title": "Test Ticket", "description": "Ticket details"}
        )
        self.assertEqual(response.status_code, 201)

    def test_create_ticket_forbidden(self):
        """Regular authenticated users should not be allowed to create tickets"""
        self.client.logout()
        self.client.login(username="agent", password="agentpass")
        data = {"title": "New Ticket", "description": "New ticket description"}
        response = self.client.post(
            "/api/tickets/",
            {"title": "Test Ticket", "description": "Ticket details"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_ticket(self):
        """Admin authenticated users should allowed to update tickets"""
        self.client.logout()
        self.client.login(username="admin", password="adminpass")
        ticket = Ticket.objects.create(title="Update Test", description="Update this")
        response = self.client.patch(
            f"/api/tickets/{ticket.id}/",
            json.dumps({"title": "Updated Title"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_ticket(self):
        """Admin authenticated users should allowed to delete tickets"""
        self.client.logout()
        self.client.login(username="admin", password="adminpass")
        ticket = Ticket.objects.create(title="Delete Test", description="Delete this")
        response = self.client.delete(f"/api/tickets/{ticket.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_agent_cannot_create_ticket(self):
        """Not Admin authenticated users should not allowed to crate tickets"""
        self.client.logout()
        self.client.login(username="agent", password="agentpass")
        response = self.client.post(
            "/api/tickets/",
            {"title": "Unauthorized", "description": "Should not be allowed"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
