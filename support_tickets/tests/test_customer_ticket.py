from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from support_tickets.models import Ticket, CustomerTicket
from support_tickets.serializers.customer_ticket_serializer import (
    CustomerTicketCreateSerializer,
)

User = get_user_model()


class CustomerTicketCreateSerializerTestCase(TestCase):
    """Test case for CustomerTicketCreateSerializer"""

    def setUp(self):
        """Set up users and tickets before each test"""

        # Create an agent user (who assigns tickets)
        self.agent_user = User.objects.create_user(
            username="agent", password="agentpass", role="agent"
        )

        # Create customer users
        self.customer1 = User.objects.create_user(
            username="customer1", password="custpass", role="customer"
        )
        self.customer2 = User.objects.create_user(
            username="customer2", password="custpass", role="customer"
        )

        # Create tickets assigned to the agent
        self.ticket1 = Ticket.objects.create(
            title="Ticket 1",
            description="Assigned to agent",
            status="assigned",
            assigned_to=self.agent_user,
        )
        self.ticket2 = Ticket.objects.create(
            title="Ticket 2",
            description="Assigned to agent",
            status="assigned",
            assigned_to=self.agent_user,
        )

        # API request context
        self.context = {"user": self.agent_user}

    ## ---------------- TEST VALID CUSTOMER TICKET CREATION ---------------- ##
    def test_valid_customer_ticket_creation(self):
        """Ensure a valid customer ticket assignment works"""
        data = {
            "customers_tickets": [
                {"customer": self.customer1.id, "ticket": self.ticket1.id},
                {"customer": self.customer2.id, "ticket": self.ticket2.id},
            ]
        }

        serializer = CustomerTicketCreateSerializer(data=data, context=self.context)
        self.assertTrue(
            serializer.is_valid(), serializer.errors
        )  # No validation errors expected

        # Save (creates customer tickets)
        serializer.save()
        self.assertEqual(
            CustomerTicket.objects.count(), 2
        )  # Two records should be created

    ## ---------------- TEST CUSTOMER VALIDATION ---------------- ##
    def test_invalid_customer_validation(self):
        """Ensure validation fails if customer ID does not exist or lacks role 'customer'"""
        # Create a non-customer user
        non_customer_user = User.objects.create_user(
            username="not_a_customer", password="pass", role="agent"
        )

        data = {
            "customers_tickets": [
                {"customer": non_customer_user.id, "ticket": self.ticket1.id}
            ]
        }

        serializer = CustomerTicketCreateSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())  # Should fail validation
        self.assertIn("customers", serializer.errors)  # Check specific validation error

    ## ---------------- TEST TICKET VALIDATION ---------------- ##
    def test_invalid_ticket_validation(self):
        """Ensure validation fails if ticket is not assigned to the user"""
        # Create a ticket assigned to another user
        another_agent = User.objects.create_user(
            username="another_agent", password="pass", role="agent"
        )
        ticket_not_assigned_to_user = Ticket.objects.create(
            title="Other Ticket",
            description="Not assigned to test user",
            status="assigned",
            assigned_to=another_agent,
        )

        data = {
            "customers_tickets": [
                {
                    "customer": self.customer1.id,
                    "ticket": ticket_not_assigned_to_user.id,
                }
            ]
        }

        serializer = CustomerTicketCreateSerializer(data=data, context=self.context)
        self.assertFalse(serializer.is_valid())  # Should fail validation
        self.assertIn("tickets", serializer.errors)  # Check for ticket validation error

    ## ---------------- TEST TRANSACTION HANDLING ---------------- ##
    def test_transaction_atomicity(self):
        """Ensure bulk creation is atomic (if one record fails, none should be created)"""
        # Simulate a scenario where one entry is valid and another is invalid (e.g., duplicate)
        CustomerTicket.objects.create(
            ticket=self.ticket1, customer=self.customer1, assigned_by=self.agent_user
        )

        data = {
            "customers_tickets": [
                {
                    "customer": self.customer1.id,
                    "ticket": self.ticket1.id,
                },  # This will fail (duplicate)
                {
                    "customer": self.customer2.id,
                    "ticket": self.ticket2.id,
                },  # This should be valid
            ]
        }

        serializer = CustomerTicketCreateSerializer(data=data, context=self.context)

        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
            serializer.save()

        # Ensure that **NO records** were created due to atomic rollback
        self.assertEqual(
            CustomerTicket.objects.count(), 1
        )  # Only the previously created one should exist
