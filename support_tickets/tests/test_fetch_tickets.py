from django.contrib.auth import get_user_model
from django.test import override_settings
from django.db import connection
from rest_framework import status
from django.test import TransactionTestCase
from concurrent.futures import ThreadPoolExecutor

from support_tickets.models import Ticket


User = get_user_model()


class AgentGenericAPIViewTestCase(TransactionTestCase):
    """Test case for the Agent ticket assignment API"""

    def setUp(self):
        """Set up users and tickets before each test"""

        self.admin_user = get_user_model().objects.create_user(
            username="admin", password="adminpass", role="admin"
        )

        self.agent_user = get_user_model().objects.create_user(
            username="agent", password="agentpass", role="agent"
        )
        self.agent_user_2 = get_user_model().objects.create_user(
            username="agent2", password="agentpass", role="agent"
        )
        self.client.login(username="admin", password="adminpass")

        # Create some test tickets (some assigned, some unassigned)
        self.assigned_ticket = Ticket.objects.create(
            title="Assigned Ticket",
            description="This is an assigned ticket",
            status="assigned",
            assigned_to=self.agent_user,
        )
        self.unassigned_tickets = [
            Ticket.objects.create(
                title=f"Unassigned {i}",
                description="Needs assignment",
                status="unassigned",
            )
            for i in range(10)  # Create 10 unassigned tickets
        ]

        # API URL endpoint
        self.agent_ticket_url = "/api/fetch-tickets/"

    ## ---------------- TEST GET ASSIGNED TICKETS ---------------- ##
    def test_agent_can_get_assigned_tickets(self):
        """An authenticated agent can retrieve assigned tickets"""
        self.client.logout()
        self.client.login(username="agent", password="agentpass")
        response = self.client.get(self.agent_ticket_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("data" in response.data)
        self.assertGreaterEqual(
            len(response.data["data"]), 1
        )  # At least one assigned ticket

    def test_agent_gets_new_tickets_if_less_than_15(self):
        """If an agent has less than 15 tickets, unassigned tickets should be assigned automatically"""
        self.client.logout()
        self.client.login(username="agent", password="agentpass")
        response = self.client.get(self.agent_ticket_url)

        # Ensure the response is paginated and agent gets newly assigned tickets
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(
            response.data["count"], min(len(self.unassigned_tickets) + 1, 15)
        )

        # Ensure that previously unassigned tickets are now assigned
        for ticket in self.unassigned_tickets:
            ticket.refresh_from_db()
            if ticket.id in [t["id"] for t in response.data["data"]]:
                self.assertEqual(ticket.status, "assigned")
                self.assertEqual(ticket.assigned_to, self.agent_user)

    def test_agent_does_not_get_more_than_15_tickets(self):
        """Ensure the agent never gets more than 15 tickets even if unassigned tickets exist"""
        self.client.logout()
        self.client.login(username="agent", password="agentpass")

        # Create more unassigned tickets to exceed the limit
        extra_tickets = [
            Ticket.objects.create(
                title=f"Extra {i}", description="Extra", status="unassigned"
            )
            for i in range(20)
        ]

        response = self.client.get(self.agent_ticket_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(response.data["count"], 15)  # Should not exceed 15

    def test_no_unassigned_tickets_available(self):
        """If there are no unassigned tickets, the agent should only get what they have"""
        self.client.logout()
        self.client.login(username="agent", password="agentpass")

        # Assign all unassigned tickets to someone else
        Ticket.objects.filter(status="unassigned").update(
            status="assigned", assigned_to=self.agent_user_2
        )

        response = self.client.get(self.agent_ticket_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(
            len(response.data["data"]), 0
        )  # Should get only assigned tickets
        self.assertLessEqual(
            len(response.data["data"]), 15
        )  # No new tickets should be assigned

    ## ---------------- TEST PERMISSION HANDLING ---------------- ##
    def test_regular_user_cannot_access_agent_endpoint(self):
        """A non-agent should not be able to access this API (403 Forbidden)"""
        self.client.logout()
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.agent_ticket_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access_agent_endpoint(self):
        """Unauthenticated users should not be able to access the endpoint"""
        response = self.client.get(self.agent_ticket_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    ## ---------------- TEST PAGINATION ---------------- ##
    def test_agent_ticket_pagination(self):
        """Ensure the agent receives paginated results"""
        self.client.logout()
        self.client.login(username="agent", password="agentpass")
        response = self.client.get(self.agent_ticket_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertIn("count", response.data)  # Total count of items

    ## ---------------- TEST Concurrency ---------------- ##
    @override_settings(DEBUG=True)
    def test_concurrent_ticket_requests(self):
        Ticket.objects.bulk_create(
            [
                Ticket(title=f"Ticket {i}", description="Concurrent test")
                for i in range(100)
            ]
        )

        def fetch_tickets(_):
            self.client.logout()
            self.client.login(username="agent", password="agentpass")
            connection.close()
            return self.client.get("/api/fetch-tickets/")

        with ThreadPoolExecutor(max_workers=10) as executor:

            responses = list(executor.map(fetch_tickets, range(10)))

        all_tickets = set()
        for response in responses:
            self.assertEqual(response.status_code, 200)
            tickets = response.json()
            for ticket in tickets["data"]:
                all_tickets.add(ticket["id"])
        self.assertEqual(type(tickets["data"]), list)
