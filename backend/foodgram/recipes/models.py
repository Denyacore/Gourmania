from calendar import c
from tkinter import E
from unicodedata import name

from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    """
    Модель тегов
    """

    name = models.CharField(max_length=100, verbose_name="Название тэга")
    color = ColorField(format="hex", verbose_name="Цветовой код")
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

    name = models.CharField(max_length=200, verbose_name="Название инградиента", db_index=True)
    measurement_unit = models.CharField(max_length=60, verbose_name="Единица измерения")

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
        max_lenght=200,
        verbose_name="Название рецепта",
    )
    image = models.ImageField(verbose_name="Фото рецепта", blank=True, upload_to="recipes/images")
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
        validators=[MinValueValidator(2, message="Время приготовления должно быть не менее 2х минут!")],
        verbose_name="Время приготовления, мин.",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэги",
    )
    pub_date = models.DateTimeField(verbose_name="Дата публикации", auto_now_add=True)

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name
