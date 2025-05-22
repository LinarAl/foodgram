from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as ModelUserAdmin

from .models import Subscription

User = get_user_model()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'subscriber',
        'user',
        'created_at'
    )
    readonly_fields = ('created_at',)
    search_fields = ('user__username',)


@admin.register(User)
class UserAdmin(ModelUserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'subscribers_count',
        'recipes_count',
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

    @admin.display(description='Кол-во подписчиков')
    def subscribers_count(self, obj):
        return obj.subscriptions.count()

    @admin.display(description='Кол-во рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()
