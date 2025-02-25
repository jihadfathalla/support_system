from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext as _


from permissions.admin_permission_class import IsAdmin
from utils.custom_paginator import paginate_queryset
from utils.get_model_by_pk import get_model_by_pk
from utils.exception_handler_decorator import handle_exceptions
from utils.custom_exception_class import CustomException

from support_tickets.models import Ticket
from support_tickets.serializers.ticket_serializer import TicketSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.list()
    serializer_class = TicketSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            self.permission_classes = [IsAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @handle_exceptions
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return paginate_queryset(request, queryset, self.get_serializer)

    @handle_exceptions
    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            instance = get_model_by_pk("support_tickets", "Ticket", pk)
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, errors=str(e)
            )

    @handle_exceptions
    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)

            return Response(
                {
                    "message": _("Ticket is successfully created"),
                    "data": response.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            raise CustomException(status_code=500, errors=str(e))

    @handle_exceptions
    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response(
                {
                    "message": _("Ticket is successfully updated"),
                    "data": response.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            raise CustomException(status_code=500, errors=str(e))

    @handle_exceptions
    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            return Response(
                {"message": _("Ticket is successfully deleted")},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            raise CustomException(status_code=500, errors=str(e))
