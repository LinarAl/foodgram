from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Subscription

User = get_user_model()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'subscriber',
        'created_at'
    )
    readonly_fields = ('created_at',)
    search_fields = ('user__username',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'date_joined'
    )
    readonly_fields = ('date_joined', 'last_login')
    list_display_links = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_active',)
