from rest_framework import serializers

from support_tickets.models import Ticket
from user.serializer import UserSerializer


class TicketSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "title", "description", "status", "created_at", "assigned_to"]
