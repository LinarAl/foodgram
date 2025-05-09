from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Subscriptions

User = get_user_model()


class SubscriptionsAdmin(admin.ModelAdmin):
    filter_horizontal = ('subscribers', )


admin.site.register(User)
admin.site.register(Subscriptions, SubscriptionsAdmin)
