"""Сериализаторы рецепта."""
from django.conf import settings
from django.db import transaction
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers

from ..validators import validate_unique_data
from .image_serializer import Base64ImageField
from .tag_serializer import TagSerializer
from .user_serializer import UserSerializer


class ShortRecipeIngredientSerializer(serializers.ModelSerializer):
    """Не полный Сериализатор для модели RecipeIngredient."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    amount = serializers.IntegerField(
        min_value=settings.AMOUNT_INGREDIENT_FIELD_MIN,
        max_value=settings.AMOUNT_INGREDIENT_FIELD_MAX
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class FullRecipeIngredientSerializer(serializers.ModelSerializer):
    """Полный сериализатор для модели RecipeIngredient и поля Ingredient."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient')
    name = serializers.CharField(
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


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


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe. Create action."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=True, allow_null=False)
    ingredients = ShortRecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True
    )
    cooking_time = serializers.IntegerField(
        min_value=settings.COOKING_TIME_FIELD_MIN,
        max_value=settings.COOKING_TIME_FIELD_MAX
    )
    author = serializers.CharField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ('id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author')
        model = Recipe

    def validate(self, data):
        ingredients = data.get('recipe_ingredients')
        tags = data.get('tags')

        validate_unique_data(ingredients, 'Ингридиенты', 'ingredient')
        validate_unique_data(tags, 'Теги')
        return data

    @staticmethod
    def create_ingredients(ingredients: list, recipe,
                           batch_size=settings.BATCH_SIZE):
        """Создание ингредиентов с помощью bulk_create."""
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient.get('ingredient'),
                    amount=ingredient.get('amount')
                ) for ingredient in ingredients
            ],
            batch_size=batch_size
        )

    @transaction.atomic()
    def create(self, validated_data):
        """Создание полей с помощью bulk_create."""
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic()
    def update(self, instance, validated_data):
        """Обновление полей при запросе PATCH."""
        tags = validated_data.pop('tags', instance.tags)
        instance.tags.set(tags)
        ingredients = validated_data.pop('recipe_ingredients', None)
        instance = super().update(instance, validated_data)
        instance.recipe_ingredient.all().delete()
        self.create_ingredients(ingredients, instance)
        return instance

    def to_representation(self, instance):
        """Возвращаем рецепт с ингредиентами в нужном формате."""
        return RecipeSerializer(
            instance=instance, context=self.context).data


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
        request = self.context.get('request', None)
        return (
            request
            and request.user.is_authenticated
            and obj.favorites.filter(user=request.user.id).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request', None)
        return bool(
            request
            and request.user.is_authenticated
            and obj.shopping_list.filter(user=request.user.id).exists()
        )

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None
