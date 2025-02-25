from rest_framework.views import APIView
from rest_framework import status
from django.utils.translation import gettext as _

from rest_framework.response import Response
from .serializer import (
    UserRegistrationSerializer,
)


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": _("User registered successfully")},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
