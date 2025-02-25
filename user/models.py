from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from utils.generate_list_cache_key import generate_list_cache_key
from config.cache_function import getKey, setKey


class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("agent", "Agent"),
        ("customer", "Customer"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="customer")

    @classmethod
    def list(cls, filter_dict={}, values_list=()):
        cache_key = generate_list_cache_key(cls.__name__, filter_dict)
        cached_data = getKey(cache_key)
        if cached_data is not None:
            if values_list:
                return cached_data.values_list(values_list, flat=True)
            return cached_data
        users = cls.objects.filter(**filter_dict)
        setKey(cache_key, users)

        if values_list:
            users = users.values_list(values_list, flat=True)
        return users
