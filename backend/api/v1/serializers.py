import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers
from recipes.models import Recipe

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(UserCreateSerializer):

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')
        model = Recipe


class CreateUserSerializer(UserCreateSerializer):

    class Meta:
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')
        model = User


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()  # True False
    avatar = serializers.SerializerMethodField()  # url

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar',)
        model = User

    def get_is_subscribed(self, obj):
        # if запрос к табл Subscriptions user=user и obj.username=subscribers тогда True
        return False

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None


class AvatarSerializer(serializers.ModelSerializer):
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
