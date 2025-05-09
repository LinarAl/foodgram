from django.contrib import admin
from .models import (Tag, Ingredient, Recipe, RecipeIngredient,
                     ShoppingList, Favorites)

# admin.site.register(AmountIngredients)


class IngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


# class TagInLine(admin.TabularInline):
#     model = Recipe.tag.through

# @admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    filter_horizontal = ('ingredients', 'tags')
    list_display = (
        'name',
        'text',
        'author',
        'cooking_time'
    )
    inlines = (
        IngredientInLine,
    )
    # list_editable = (
    #     'cooking_time',
    # )
    search_fields = ('author__username', 'name')
    list_filter = ('tags',)


class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name', 'unit')


class FavoritesAdmin(admin.ModelAdmin):
    filter_horizontal = ('recipes', )


class ShoppingListAdmin(admin.ModelAdmin):
    filter_horizontal = ('recipes', )


admin.site.register(Tag)

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)

admin.site.register(Favorites, FavoritesAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
