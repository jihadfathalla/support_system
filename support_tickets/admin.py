from django.contrib import admin

from .models import Ticket, CustomerTicket

admin.site.register(Ticket)
admin.site.register(CustomerTicket)
