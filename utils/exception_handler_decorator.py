from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response

from .constants import MESSAGE, VALIDATION_ERRORS

from .custom_exception_class import CustomException


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CustomException as e:
            return Response(
                {MESSAGE: e.message, VALIDATION_ERRORS: e.errors}, status=e.status_code
            )

        except Exception as e:
            if not settings.DEBUG:
                return Response(
                    {
                        MESSAGE: _("Something went wrong, please contact support."),
                        VALIDATION_ERRORS: None,
                    },
                    status=500,
                )
            raise e

    return wrapper
