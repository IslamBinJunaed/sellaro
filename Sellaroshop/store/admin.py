from django.contrib import admin
from .models import StoreLocation

@admin.register(StoreLocation)
class StoreLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'phone', 'is_active']
    list_filter = ['city', 'state', 'is_active']
    search_fields = ['name', 'address', 'city']
    list_editable = ['is_active']
    