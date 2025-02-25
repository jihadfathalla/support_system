from celery import shared_task
import time

from support_tickets.serializers.agent_serializer import AgentSerializer


@shared_task
def fetch_ticket_data(user):
    return AgentSerializer().fetch_tickets(user)
