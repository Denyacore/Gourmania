from re import search

from django.db import transaction
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                            ShoppingCart, Tag)
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
        fields = ("email", "id", "username", "first_name",
                  "last_name", "is_subscribed")

    def get_is_subscribed(self, obj: User):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
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

    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", read_only=True)
    name = serializers.SlugRelatedField(
        source="ingredient", read_only=True, slug_field="name")
    measurement_unit = serializers.SlugRelatedField(
        source="ingredient", read_only=True, slug_field="measurement_unit")

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

    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientsInRecipe
        fields = (
            "id",
            "amount",
        )

    def validate_amount(self, data):
        if float(data) < 0.001:
            raise ValidationError(
                {"ingredients": ("Ингредиента должно быть не менее 0.001."), "msg": data})
        return data

    @transaction.atomic
    def create(self, validated_data):
        return IngredientsInRecipe.objects.create(
            ingredient=validated_data.get("id"), amount=validated_data.get("amount")
        )


class CreateRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания и изменения рецепта
    """
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(use_url=True, max_length=None)
    author = UserSerializer(read_only=True)
    ingredients = CreateIngredientsInRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    @transaction.atomic
    def create_ingredients(self, recipe, ingredients):
        IngredientsInRecipe.objects.bulk_create([
            IngredientsInRecipe(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=ingredient['ingredient'],
            ) for ingredient in ingredients
        ])

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise ValidationError(
                    'Есть задублированные ингредиенты!'
                )
            ingredients_list.append(ingredient_id)
        if data['cooking_time'] < 1:
            raise ValidationError(
                'Время приготовления должно быть не менее 1 минуты!'
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=request.user,
            **validated_data
        )
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = instance
        IngredientsInRecipe.objects.filter(recipe=recipe).delete()
        self.create_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return GetRecipeSerializer(
            instance,
            context={
                'request': self.context.get('request'),
            }
        ).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """
    Сериализатор короткой карточки рецепта
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор списка покупок
    """
    class Meta:
        model = ShoppingCart
        field = (
            'user',
            'recipe',
        )
        validators = UniqueTogetherValidator(
            queryset=ShoppingCart.objects.all(),
            fields=('user', 'recipe'),
            message='Рецепт уже в корзине'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe',
        )
        validators = UniqueTogetherValidator(
            queryset=Favorite.objects.all(),
            fields=('user', 'recipe'),
            message='Рецепт уже в избранном'
        )


class FollowersSerializer(serializers.ModelSerializer):
    """
    Сериализатор получения подписок со списком рецептов авторов
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_recipes(self, author):
        queryset = self.context.get('request')
        recipes_limit = queryset.query_params.get('recipes_limit')
        if not recipes_limit:
            return RecipeShortSerializer(
                Recipe.objects.filter(author=author),
                many=True, context={'request': queryset}
            ).data
        return RecipeShortSerializer(
            Recipe.objects.filter(author=author)[:int(recipes_limit)],
            many=True,
            context={'request': queryset}
        ).data

    def get_is_subscribed(self, author):
        return Follow.objects.filter(
            user=self.context.get('request').user,
            author=author
        ).exists()


class FollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор подписки на пользователя
    """
    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны'
            )
        ]

    def validate(self, data):
        get_object_or_404(User, username=data['author'])
        if self.context['request'].user == data['author']:
            raise ValidationError({
                'Нельзя подписаться на себя'
            })
        return data
