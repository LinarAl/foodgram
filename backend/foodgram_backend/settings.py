"""Foodgram settings."""

import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', get_random_secret_key())

DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'http://127.0.0.1:8000').split(' ')

CSRF_TRUSTED_ORIGINS = os.getenv(
    'CSRF_TRUSTED_ORIGINS', 'http://127.0.0.1:8000').split(' ')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'rest_framework.authtoken',
    'djoser',
    'recipes.apps.RecipesConfig',
    'users.apps.UsersConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'django'),
        'USER': os.getenv('POSTGRES_USER', 'django'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', 5432)
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'users.User'

DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
        'user_list': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
    },
    'SERIALIZERS': {
        'user_create': 'api.serializers.user_serializer.CreateUserSerializer',
        'user': 'api.serializers.user_serializer.UserSerializer',
        'current_user': 'api.serializers.user_serializer.UserSerializer',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    )
}

# Field limitations
# Forbidden values
FORBIDDEN_USERNAMES = ('me',)
# Models:
# Users
USERNAME_FIELD_LENGTH = 150
FIRST_NAME_FIELD_LENGTH = 150
LAST_NAME_FIELD_LENGTH = 150
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
# Pagination
DEFAULT_PAGE_SIZE = 10
# create/update ingredients batch
BATCH_SIZE = 100
# SubscriptionSerializer base recipes_limit
BASE_RECIPES_LIMIT_SUBSCRIPTION = 5
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

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static_back/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# fixture path
FIXTURE_PATH = BASE_DIR / 'fixtures_data'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
