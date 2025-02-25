from rest_framework import serializers

from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]

    # def validate_email(self, value):
    #     try:
    #         validate_email(value)
    #     except ValidationError:
    #         raise serializers.ValidationError(_("email cannot be empty"))
    #     return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data["role"],
        )
        return user
