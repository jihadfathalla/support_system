from rest_framework import serializers
from django.db import transaction

from support_tickets.models import Ticket


class AgentSerializer(serializers.Serializer):

    def fetch_tickets(self, user):
        assigned_tickets = list(
            Ticket.list({"assigned_to": user, "status": "assigned"})
        )
        if len(assigned_tickets) < 15:
            tickets_needed = 15 - len(assigned_tickets)

            with transaction.atomic():
                new_tickets = list(
                    Ticket.objects.filter(status="unassigned")
                    .select_for_update(skip_locked=True)
                    .order_by("created_at")[:tickets_needed]
                )
                if new_tickets:

                    Ticket.objects.filter(
                        id__in=[ticket.id for ticket in new_tickets]
                    ).update(status="assigned", assigned_to=user)

                    assigned_tickets.extend(new_tickets)
                else:
                    return []

        return assigned_tickets
