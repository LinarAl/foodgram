"""Модели приложения recipes."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class AbstractNameModel(models.Model):
    """Абстрактная модель с полем name."""

    name = models.CharField(
        max_length=settings.TITLE_FIELD_MAX_LENGTH,
        unique=True,
        verbose_name=_('Название')
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Tag(AbstractNameModel):
    """Модель тега."""

    slug = models.SlugField(
        max_length=settings.SLUG_FIELD_MAX_LENGTH,
        unique=True,
        db_index=True,
        verbose_name=_('slug')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ('name',)


class Ingredient(AbstractNameModel):
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

    measurement_unit = models.CharField(
        max_length=settings.MEASUREMENT_UNIT_FIELD_MAX_LENGTH,
        choices=UnitChoices.choices,
        verbose_name=_('Единица измерения')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'

    class Meta:
        verbose_name = _('Ингридиент')
        verbose_name_plural = _('Ингридиенты')


class RecipeIngredient(models.Model):
    """Промежуточная модель с количеством ингридиента."""

    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт'),
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=_('Ингридиент'),

    )
    amount = models.IntegerField(
        verbose_name=_('Количество'),
        validators=[
            MinValueValidator(
                settings.AMOUNT_INGREDIENT_FIELD_MIN,
                message=_(
                    f'Значение должно быть меньше \n'
                    f'{settings.AMOUNT_INGREDIENT_FIELD_MIN}')
            ),
            MaxValueValidator(
                settings.AMOUNT_INGREDIENT_FIELD_MAX,
                message=_(
                    f'Значение должно быть больше \n'
                    f'{settings.AMOUNT_INGREDIENT_FIELD_MAX}')
            )
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe'
            )
        ]
        ordering = ('recipe', 'ingredient')
        verbose_name = _('Количество ингридиента')
        verbose_name_plural = _('Количество ингридиентов')
        default_related_name = 'recipe_ingredients'

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class Recipe(AbstractNameModel):
    """Модель рецепта."""

    name = models.CharField(
        max_length=settings.RECIPE_NAME_FIELD_MAX_LENGTH,
        db_index=True,
        verbose_name=_('Название')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Автор'),
        related_name='recipes'
    )
    image = models.ImageField(
        upload_to='recipe/images/',
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
        verbose_name=_('Время приготовления в минутах'),
        validators=[
            MinValueValidator(
                settings.COOKING_TIME_FIELD_MIN,
                message=_(
                    f'Значение должно быть меньше \n'
                    f'{settings.COOKING_TIME_FIELD_MIN}')
            ),
            MaxValueValidator(
                settings.COOKING_TIME_FIELD_MAX,
                message=_(
                    f'Значение должно быть больше \n'
                    f'{settings.COOKING_TIME_FIELD_MAX}')
            )
        ]
    )
    link = models.CharField(
        max_length=settings.LINK_FIELD_MAX_LENGTH,
        unique=True,
        blank=True,
        verbose_name=_('Короткая ссылка')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        ordering = ('-created_at',)

    def save(self, *args, **kwargs):
        if not self.link:
            self.link = get_random_string(
                length=settings.LINK_FIELD_MAX_LENGTH)
            while Recipe.objects.filter(link=self.link).exists():
                self.link = get_random_string(
                    length=settings.LINK_FIELD_MAX_LENGTH)
        super().save(*args, **kwargs)


class AbstractUserRecipesModel(models.Model):
    """Абстрактная модель с полем пользователь и рецепт."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь')
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'Пользователь: {self.user}'


class ShoppingList(AbstractUserRecipesModel):
    """Модель списка покупок."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_list'
            )
        ]
        verbose_name = _('Список покупок')
        verbose_name_plural = _('Список покупок')
        default_related_name = 'shopping_list'
        ordering = ('-created_at',)


class Favorites(AbstractUserRecipesModel):
    """Модель избранного."""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorites'
            )
        ]
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранное')
        default_related_name = 'favorites'
        ordering = ('-created_at',)
