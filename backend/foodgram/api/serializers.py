from re import search

from django.db import transaction
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Favorite, Ingredient, IngredientsInRecipe, Recipe, ShoppingCart, Tag
from requests import request
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator
from users.models import Follow, User


class UsersSerializer(UserSerializer):
    """
    Сериализатор пользователя с отметкой о подписке
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name", "is_subscribed")

    def get_is_subscribed(self, obj: User):
        request = self.context.get("request")
        if not request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор тегов
    """

    class Meta:
        model = Tag
        fields = "__all__"


class IngridientSerializer(serializers.ModelSerializer):
    """
    Сериализатор инградиентов
    """

    class Meta:
        model = Ingredient
        fields = "__all__"


class GetIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор получения ингредиентов для рецептов
    """

    id = serializers.PrimaryKeyRelatedField(source="ingredient", read_only=True)
    name = serializers.SlugRelatedField(source="ingredient", read_only=True, slug_field="name")
    measurement_unit = serializers.SlugRelatedField(source="ingredient", read_only=True, slug_field="measurement_unit")

    class Meta:
        model = IngredientsInRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class GetRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор получения рецептов, дополненный полями
    наличия в списке покупок и избранном
    """

    image = Base64ImageField(use_url=True, max_length=None)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = GetIngredientsInRecipeSerializer(
        many=True,
        read_only=True,
        source="ingridients_in_recipe",
    )
    author = UsersSerializer(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=request.user, recipe__id=obj.id).exists()


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания и изменения ингредиентов в рецептах
    с проверкой количества
    """

    id = serializers.PrimaryKeyRelatedField(source="ingredient", queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientsInRecipe
        fields = (
            "id",
            "amount",
        )

    def validate_amount(self, data):
        if float(data) < 0.001:
            raise ValidationError({"ingredients": ("Ингредиента должно быть не менее 0.001."), "msg": data})
        return data

    @transaction.atomic
    def create(self, validated_data):
        return IngredientsInRecipe.objects.create(
            ingredient=validated_data.get("id"), amount=validated_data.get("amount")
        )
