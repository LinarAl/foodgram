"""Сериализатор для подписок."""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from foodgram_backend.constants import BASE_RECIPES_LIMIT_SUBSCRIPTION
from users.models import Subscription
from .recipe_serializer import ShortRecipeSerializer
from .user_serializer import UserSerializer

User = get_user_model()


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для отображения подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')
        model = User

    def get_recipes_limit(self):
        """Устанавливаем лимит для рецептов."""
        request = self.context.get('request')
        limit = BASE_RECIPES_LIMIT_SUBSCRIPTION
        if not request:
            return limit
        try:
            return int(request.query_params.get('recipes_limit', limit))
        except (ValueError, TypeError):
            return limit

    def get_recipes(self, obj):
        recipes_limit = self.get_recipes_limit()
        recipes = obj.recipes.all()[:recipes_limit]

        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Subscription."""

    class Meta:
        fields = ('subscriber', 'user')
        model = Subscription

    def validate(self, data):
        if data.get('subscriber') == data.get('user'):
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')
        return data

    def to_representation(self, instance):
        return SubscriptionSerializer(
            instance.user, context=self.context).data
