from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import SellerProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Marketplace', {'fields': ('role', 'city')}),
    )
    list_display = ('username', 'email', 'role', 'is_staff')


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('business_name', 'user__username')
