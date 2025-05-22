from django.contrib import admin

from foodgram_backend.constants import OBJECTS_PER_PAGE
from .models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                     ShoppingList, Tag)


class IngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


@admin.register(Tag)
class Tagadmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
        'created_at'
    )
    readonly_fields = ('created_at',)
    search_fields = (
        'name',
        'slug',
    )
    list_display_links = (
        'id',
        'name',
        'slug',
    )
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
        'created_at'
    )
    readonly_fields = ('created_at',)
    search_fields = (
        'name',
    )
    list_display_links = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = ('measurement_unit',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    filter_horizontal = ('ingredients', 'tags')
    list_display = (
        'id',
        'name',
        'text',
        'author',
        'cooking_time',
        'favorites_count',
        'created_at'
    )
    readonly_fields = ('link', 'favorites_count', 'created_at', 'updated_at')
    inlines = (
        IngredientInLine,
    )
    list_display_links = (
        'id',
        'name',
        'text'
    )
    search_fields = ('author__username', 'name')
    list_filter = ('tags',)

    @admin.display(description='В избранном (кол-во)')
    def favorites_count(self, obj):
        return obj.favorites.count()


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
        'created_at'
    )
    list_display_links = (
        'id',
        'user',
        'recipe'
    )
    readonly_fields = ('created_at',)
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)
    list_per_page = OBJECTS_PER_PAGE


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
        'created_at'
    )
    list_display_links = (
        'id',
        'user',
        'recipe'
    )
    readonly_fields = ('created_at',)
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)
    list_per_page = OBJECTS_PER_PAGE
