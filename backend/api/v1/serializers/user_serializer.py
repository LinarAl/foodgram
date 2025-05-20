"""Сериализаторы пользователей."""
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers
from users.models import Subscription

from .image_serializer import Base64ImageField

User = get_user_model()


class CreateUserSerializer(UserCreateSerializer):
    """Сериализатор для модели User. Creat action."""

    class Meta:
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')
        model = User


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar',)
        model = User

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        return bool(
            current_user.id
            and Subscription.objects.filter(
                subscriber=current_user, user=obj).exists()
        )

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара для модели User."""

    avatar = Base64ImageField(required=False, allow_null=True)

    def validate(self, data):
        example_value = {
            'field_name': [
                'Введите поле avatar.'
            ]
        }
        if not data:
            raise serializers.ValidationError(example_value)
        return data

    class Meta:
        fields = ('avatar',)
        model = User
