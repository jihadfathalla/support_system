from rest_framework.permissions import BasePermission


class AllowAnyForSpecificEndpoints(BasePermission):
    def has_permission(self, request, view):
        if view.__class__.__name__ in [
            "UserRegistrationView",
            "LoginView",
        ]:
            return True
        return request.user and request.user.is_authenticated
