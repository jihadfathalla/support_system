from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.ticket_view import TicketViewSet
from .views.customer_ticket_view import CustomerTicketViewSet
from .views.agent_view import AgentGenericAPIView


app_name = "api"

router = DefaultRouter()
router.register(r"tickets", TicketViewSet, basename="ticket")
router.register(r"customers", CustomerTicketViewSet, basename="customer-ticket")

urlpatterns = [
    path("fetch-tickets/", AgentGenericAPIView.as_view(), name="fetch-tickets"),
    path("", include(router.urls)),
]
