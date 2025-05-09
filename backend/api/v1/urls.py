from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter

# auth_urls = [
#     path('signup/', views.APISignUpView.as_view(), name='signup'),
#     path('token/', views.TokenObtainView.as_view(), name='token_obtain_pair'),
# ]

router_v1 = DefaultRouter()

router_v1.register('users', views.UsersViewSet, basename='users')
router_v1.register('tags', views.TagViewSet, basename='tags')

urlpatterns = [
    # path('auth/', include(auth_urls)),
    path('', include(router_v1.urls)),
    # path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
