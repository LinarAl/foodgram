"""Сериализаторы."""
import base64

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from recipes.models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from rest_framework import serializers
from users.models import Subscription

from .validators import validate_unique_data

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Сериализатор для картинки Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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
                user=obj, subscriber=current_user).exists()
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


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        fields = ('id', 'name', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class ShortRecipeIngredientSerializer(serializers.ModelSerializer):
    """Не полный Сериализатор для модели RecipeIngredient."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class FullRecipeIngredientSerializer(serializers.ModelSerializer):
    """Полный сериализатор для модели RecipeIngredient и поля Ingredient."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe. Create action."""
    image = Base64ImageField(required=True, allow_null=False)
    ingredients = ShortRecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True
    )

    class Meta:
        fields = ('id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')
        model = Recipe

    def validate(self, data):
        ingredients = data.get('recipe_ingredients')
        tags = data.get('tags')

        validate_unique_data(ingredients, 'Ингридиенты', 'ingredient')
        validate_unique_data(tags, 'Теги')
        return data

    @transaction.atomic()
    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient.get('ingredient'),
                    amount=ingredient.get('amount')
                ) for ingredient in ingredients
            ],
            batch_size=settings.BATCH_SIZE
        )
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic()
    def update(self, instance, validated_data):
        """Обновление полей с помощью bulk_update при запросе PATCH.

        exist_ingr - необновленные объекты recipe_ingredient.
        exist_dict_id_ingr - словарь где ключ - id необновленного ингредиента,
        значение - необновленный объект recipe_ingredient.
        new_ingr - множество(set) id новых ингредиентов.
        to_delete - объекты recipe_ingredient, которые нужно удалить.
        updates - список ингридиентов для обновления.
        new_ingredients - список ингридиентов для создания.
        """
        tags = validated_data.pop('tags', instance.tags)
        instance.tags.set(tags)
        ingredients = validated_data.pop('recipe_ingredients', None)
        instance = super().update(instance, validated_data)

        exist_ingr = instance.recipe_ingredient.all()
        exist_dict_id_ingr = {
            r_i_obj.ingredient_id: r_i_obj for r_i_obj in exist_ingr}
        new_ingr = {
            ingredient['ingredient'].id for ingredient in ingredients}

        to_delete = exist_ingr.exclude(ingredient_id__in=new_ingr)
        if to_delete.exists():
            to_delete.delete()

        updates = []
        new_ingredients = []

        for ingredient in ingredients:
            ingredient_id = ingredient['ingredient'].id
            if ingredient_id in exist_dict_id_ingr:
                obj = exist_dict_id_ingr[ingredient_id]
                obj.amount = ingredient['amount']
                updates.append(obj)
            else:
                new_ingredients.append(
                    RecipeIngredient(
                        recipe=instance,
                        ingredient=ingredient.get('ingredient'),
                        amount=ingredient.get('amount')
                    )
                )

        if updates:
            RecipeIngredient.objects.bulk_update(
                updates,
                fields=['amount'],
                batch_size=settings.BATCH_SIZE
            )

        if new_ingredients:
            RecipeIngredient.objects.bulk_create(
                new_ingredients,
                batch_size=settings.BATCH_SIZE
            )
        return instance

    def to_representation(self, instance):
        """Возвращаем рецепт с ингредиентами в нужном формате."""
        representation = RecipeSerializer(
            instance=instance, context=self.context).data
        return representation


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    ingredients = FullRecipeIngredientSerializer(
        source='recipe_ingredient', many=True, read_only=True)
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        model = Recipe

    def get_is_favorited(self, obj):
        current_user = self.context['request'].user.id
        return bool(
            current_user
            and obj.favorites.filter(user=current_user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context['request'].user.id
        return bool(
            current_user
            and obj.shopping_list.filter(user=current_user).exists()
        )

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe для ShoppingListSerializer и
    FavoritesSerializer."""

    image = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShoppingList."""

    class Meta:
        fields = ('user', 'recipe')
        model = ShoppingList

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data


class FavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Favorites."""

    class Meta:
        fields = ('user', 'recipe')
        model = Favorites

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data


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
        limit = settings.BASE_RECIPES_LIMIT_SUBSCRIPTION
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
        fields = ('user', 'subscriber')
        model = Subscription

    def to_representation(self, instance):
        return SubscriptionSerializer(
            instance.subscriber, context=self.context).data
