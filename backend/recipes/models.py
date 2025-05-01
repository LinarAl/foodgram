"""Модели приложения recipes."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class AbstractTitleModel(models.Model):
    """Абстрактная модель с полем title."""

    name = models.CharField(
        max_length=settings.TITLE_FIELD_MAX_LENGTH,
        verbose_name=_('Название')
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Tag(AbstractTitleModel):
    """Модель тега."""

    slug = models.SlugField(
        max_length=settings.SLUG_FIELD_MAX_LENGTH,
        unique=True,
        verbose_name=_('slug')
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')


class Ingredient(AbstractTitleModel):
    """Модель ингридиента."""

    class UnitChoices(models.TextChoices):
        GRAMS = settings.GRAMS_UNIT, _('Граммы')
        MILLILITERS = settings.MILLILITERS_UNIT, _('Миллилитры')
        QUANTITY = settings.QUANTITY_UNIT, _('Количество в штуках')
        TEASPOON = settings.TEASPOON_UNIT, _('Чайная ложка')
        TABLESPOON = settings.TABLESPOON_UNIT, _('Столовая ложка')
        PINCH = settings.PINCH_UNIT, _('Щепотка')
        DROP = settings.DROP_UNIT, _('Капля')
        CUP = settings.CUP_UNIT, _('Стакан')
        JAR = settings.JAR_UNIT, _('Банка')
        TO_TASTE = settings.TO_TASTE_UNIT, _('По вкусу')

    unit = models.CharField(
        max_length=settings.UNIT_FIELD_MAX_LENGTH,
        choices=UnitChoices.choices,
        verbose_name=_('Единица измерения')
    )

    def __str__(self):
        return f'{self.name} {self.unit}'

    class Meta:
        verbose_name = _('Ингридиент')
        verbose_name_plural = _('Ингридиенты')


class RecipeIngredient(models.Model):
    """Промежуточная модель с количеством ингридиента."""

    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт')
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=_('Ингридиент')
    )
    amount = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name=_('Количество')
    )

    class Meta:
        verbose_name = _('Количество ингридиента')
        verbose_name_plural = _('Количество ингридиентов')

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class Recipe(AbstractTitleModel):
    """Модель рецепта."""

    name = models.CharField(
        max_length=settings.RECIPE_NAME_FIELD_MAX_LENGTH,
        verbose_name=_('Название')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Автор')
    )
    image = models.ImageField(
        upload_to='recipe/images/',
        null=True,
        blank=True,  # !!!!!!!!!!
        default=None,
        verbose_name=_('Картинка')
    )
    text = models.TextField(verbose_name=_('Описание'))
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name=_('Ингридиенты')
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_('Тег')
    )
    cooking_time = models.IntegerField(
        verbose_name=_('Время приготовления в минутах')
    )

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')


class AbstractUserRecipesModel(models.Model):
    """Абстрактная модель с полем пользователь и рецепт."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь')
    )
    recipes = models.ManyToManyField(
        Recipe,
        verbose_name=_('Рецепт')
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'Пользователь: {self.user}'


class ShoppingList(AbstractUserRecipesModel):
    """Модель списка покупок."""

    class Meta:
        verbose_name = _('Список покупок')
        verbose_name_plural = _('Список покупок')


class Favorites(AbstractUserRecipesModel):
    """Модель избранного."""

    class Meta:
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранное')


class Subscriptions(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь')
    )

    subscribers = models.ManyToManyField(
        User,
        verbose_name=_('Подписчик'),
        related_name='subscribers'
    )

    class Meta:
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
