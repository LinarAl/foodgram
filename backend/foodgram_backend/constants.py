"""Константы для приложений."""
# Forbidden values
FORBIDDEN_USERNAMES = ('me',)
# Field limitations:
# Model users:
USERNAME_FIELD_LENGTH = 150
FIRST_NAME_FIELD_LENGTH = 150
LAST_NAME_FIELD_LENGTH = 150
# Model recipes:
# Name
TITLE_FIELD_MAX_LENGTH = 128
# Tag
SLUG_FIELD_MAX_LENGTH = 32
# Ingredient
MEASUREMENT_UNIT_FIELD_MAX_LENGTH = 64
# RecipeIngredient
AMOUNT_INGREDIENT_FIELD_MIN = 1
AMOUNT_INGREDIENT_FIELD_MAX = 1000000
# Recipe
RECIPE_NAME_FIELD_MAX_LENGTH = 256
COOKING_TIME_FIELD_MIN = 1
COOKING_TIME_FIELD_MAX = 10080
LINK_FIELD_MAX_LENGTH = 8
# Serializers:
# recipe, create/update ingredients batch
BATCH_SIZE = 100
# subscription base recipes_limit
BASE_RECIPES_LIMIT_SUBSCRIPTION = 5
# Pagination
DEFAULT_PAGE_SIZE = 6
PAGE_SIZE_PARAM = 'page'
PAGE_SIZE_QUERY_PARAM = 'limit'
PAGE_SIZE_MAX_LIMIT = 100
# Admin zone
# recipes
OBJECTS_PER_PAGE = 30

# Recipes settings: Ingredient UnitChoices
GRAMS_UNIT = 'г'
MILLILITERS_UNIT = 'мл'
QUANTITY_UNIT = 'шт.'
TEASPOON_UNIT = 'ч. л.'
TABLESPOON_UNIT = 'ст. л.'
PINCH_UNIT = 'щепотка'
DROP_UNIT = 'капля'
CUP_UNIT = 'стакан'
JAR_UNIT = 'банка'
TO_TASTE_UNIT = 'по вкусу'
