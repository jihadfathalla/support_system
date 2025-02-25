from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext as _


from permissions.agent_permission_class import IsAgent
from permissions.admin_permission_class import IsAdmin

from utils.custom_paginator import paginate_queryset
from utils.exception_handler_decorator import handle_exceptions
from utils.custom_exception_class import CustomException

from support_tickets.models import CustomerTicket
from support_tickets.serializers.customer_ticket_serializer import (
    CustomerTicketCreateSerializer,
    CustomerTicketListSerializer,
)


class CustomerTicketViewSet(viewsets.ModelViewSet):
    queryset = CustomerTicket.objects.all()
    serializer_class = CustomerTicketCreateSerializer

    def get_permissions(self):
        if self.action in ["create", "list"]:
            self.permission_classes = [IsAdmin | IsAgent]

        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @handle_exceptions
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return paginate_queryset(request, queryset, CustomerTicketListSerializer)

    @handle_exceptions
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"user": request.user}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": _("Tickets is successfully assigned to Customers")},
                status=status.HTTP_201_CREATED,
            )
        raise CustomException(status_code=400, errors=serializer.errors)
