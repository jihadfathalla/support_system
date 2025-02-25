from rest_framework.generics import GenericAPIView

from utils.custom_paginator import paginate_queryset
from permissions.agent_permission_class import IsAgent

from support_tickets.serializers.ticket_serializer import TicketSerializer
from ..tasks import fetch_ticket_data


class AgentGenericAPIView(GenericAPIView):
    permission_classes = [IsAgent]

    def get(self, request):
        assigned_tickets = fetch_ticket_data(request.user)
        return paginate_queryset(
            request,
            assigned_tickets,
            TicketSerializer,
        )
