from rest_framework import serializers
from django.db import transaction


from user.models import User
from support_tickets.models import Ticket, CustomerTicket


class CustomerTicketCreateSerializer(serializers.ModelSerializer):
    customers_tickets = serializers.ListField(required=True)

    class Meta:
        model = CustomerTicket
        fields = ["customers_tickets"]

    def validate_customers(self, customers):
        queryset = User.list({"role": "customer"}, ("id"))
        return set(customers).issubset(set(queryset))

    def validate_tickets(self, tickets, user):
        queryset = Ticket.list({"assigned_to": user, "status": "assigned"}, ("id"))
        return set(tickets).issubset(set(queryset))

    def validate(self, data):
        user = self.context.get("user")
        errors = {}
        customers = list(customer["customer"] for customer in data["customers_tickets"])
        tickets = list(entry["ticket"] for entry in data["customers_tickets"])

        if not self.validate_customers(customers):
            errors["customers"] = (
                "customers ids must be a FK of users have role customer."
            )

        if not self.validate_tickets(tickets, user):
            errors["tickets"] = "tickets ids must assigned to user."
        if errors:
            raise serializers.ValidationError(errors)
        return data

    def create(self, validated_data):

        user = self.context.get("user")
        customers_tickets = validated_data.pop("customers_tickets", [])
        with transaction.atomic():
            data = self.create_customer_ticket(customers_tickets, user)
        return data

    def create_customer_ticket(self, customers_tickets, user):
        created_records = []
        try:
            for customer in customers_tickets:
                obj = CustomerTicket(
                    ticket_id=customer["ticket"],
                    customer_id=customer["customer"],
                    assigned_by=user,
                )
                created_records.append(obj)
            return CustomerTicket.objects.bulk_create(created_records)
        except :
            raise serializers.ValidationError({"ticket": "this ticket id already used"})


class CustomerTicketListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerTicket
        fields = "__all__"

    def to_representation(self, instance):
        action = self.context.get("action", None)
        if action == "list":
            representation = super().to_representation(instance)
            representation["customer_name"] = instance.customer.username
            representation["assigned_by_name"] = instance.assigned_by.username
            return representation
        return super().to_representation(instance)
