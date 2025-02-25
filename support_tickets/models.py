from django.db import models
from utils.generate_list_cache_key import generate_list_cache_key
from config.cache_function import getKey, setKey
from user.models import User


class Ticket(models.Model):
    STATUS_CHOICES = (
        ("unassigned", "Unassigned"),
        ("assigned", "Assigned"),
        ("sold", "Sold"),
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="unassigned", db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tickets",
        db_index=True,
    )

    @classmethod
    def list(cls, filter_dict={}, values_list=()):
        cache_key = generate_list_cache_key(cls.__name__, filter_dict)
        cached_data = getKey(cache_key)
        if cached_data is not None:
            if values_list:
                return cached_data.values_list(values_list, flat=True)
            return cached_data
        tickets = cls.objects.filter(**filter_dict).order_by("created_at")

        setKey(cache_key, tickets)
        if values_list:
            tickets = tickets.values_list(values_list, flat=True)
        return tickets


class CustomerTicket(models.Model):
    ticket = models.OneToOneField(
        Ticket, on_delete=models.CASCADE, related_name="customer_ticket"
    )
    assigned_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="assigned_tickets"
    )
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="assigned_customer"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.ticket.id} assigned to {self.customer.username}"
