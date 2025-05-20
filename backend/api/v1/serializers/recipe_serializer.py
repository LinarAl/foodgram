"""Сериализаторы рецепта."""
from django.conf import settings
from django.db import transaction
from recipes.models import Ingredient, Recipe, RecipeIngredient
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
