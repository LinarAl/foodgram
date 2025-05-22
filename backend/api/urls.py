from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.ingredient_view import IngredientViewSet
from .views.recipe_view import RecipeViewSet
from .views.tag_view import TagViewSet
from .views.user_view import UsersViewSet

router = DefaultRouter()

router.register('users', UsersViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet,
                basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
