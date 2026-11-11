from django.contrib import admin
from .models import Establishment, Ticket

@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "city", "is_active")
    list_filter = ("category", "city", "is_active")
    search_fields = ("name", "city")

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("number", "user", "establishment", "status", "created_at")
    list_filter = ("status", "establishment", "created_at")
    search_fields = ("user__username", "establishment__name")
    readonly_fields = ("created_at",)
