from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router_v1 = DefaultRouter()

router_v1.register('users', views.UsersViewSet, basename='users')
router_v1.register('tags', views.TagViewSet, basename='tags')
router_v1.register('ingredients', views.IngredientViewSet,
                   basename='ingredients')
router_v1.register('recipes', views.RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
