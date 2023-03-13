from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    """
    Модель тегов
    """
    name_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_а-яА-Я]+$',
        message='Разрешены только буквы, цифры и символ подчеркивания',
        code='invalid_tag_name'
    )

    color_validator = RegexValidator(
        regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        message='Значение должно быть в формате HEX (например, #FF0000)',
        code='invalid_color_code'
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Название тэга",
        validators=[name_validator]
        )
    color = ColorField(format="hex",
                       verbose_name="Цветовой код",
                       validators=[color_validator]
                       )
    slug = models.SlugField(verbose_name="Slug", unique=True)

    class Meta:
        ordering = ("-name",)
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """
    Модель инградиентов
    """

    name = models.CharField(
        max_length=200, verbose_name="Название инградиента", db_index=True)
    measurement_unit = models.CharField(
        max_length=60, verbose_name="Единица измерения")

    class Meta:
        ordering = ("-name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    """
    Модель рецептов
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор рецепта",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта",
    )
    image = models.ImageField(
        verbose_name="Фото рецепта", blank=True, upload_to="recipes/images")
    text = models.TextField(
        verbose_name="Описание рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientsInRecipe",
        verbose_name="Инградиенты рецепта",
        related_name="recipe",
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1, message="Время приготовления должно быть не менее 1 минуты!")],
        verbose_name="Время приготовления, мин.",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True)

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientsInRecipe(models.Model):
    """
    Промежуточная модель для связи рецептов и ингредиентов
    """

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиенты для рецепта")
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт")
    amount = models.FloatField(
        default=1,
        validators=[MinValueValidator(
            0.001, message="Ингредиента должно быть не менее 0.001.")],
        verbose_name="Количество ингредиента",
    )

    class Meta:
        default_related_name = "ingridients_in_recipe"
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"
        constraints = [models.UniqueConstraint(
            fields=["recipe", "ingredient"], name="unique_recipe")]

    def __str__(self):
        return f"{self.recipe}: {self.ingredient} – {self.amount}"


class ShoppingCart(models.Model):
    """
    Модель списка покупок
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        default_related_name = "shopping_cart"
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Список покупок"
        constraints = [models.UniqueConstraint(
            fields=["user", "recipe"], name="unique_shopping_cart")]


class Favorite(models.Model):
    """
    Модель избранных рецептов
    """

    recipe = models.ForeignKey(
        Recipe,
        related_name="in_favorited",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("user",)
        default_related_name = "favorite"
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранное"
        constraints = [models.UniqueConstraint(
            fields=["recipe", "user"], name="unique_favorite")]
