from django.shortcuts import render, get_object_or_404
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Follow,User
from .serializers import (TagSerializer, IngridientSerializer, 
                         FollowSerializer, GetRecipeSerializer, 
                         CreateRecipeSerializer, ShopingcartSerializer,
                         FavoritedSerializer)

from djoser.views import UserViewSet

from .utils import download_shopping_cart
from .filters import RecipeFilter
from .pagination import RecipePagination
from .permissions import IsAdminOrAuthorOrReadOnlyPermission

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters, status
from rest_framework.response import Response


class TagViewSet(ModelViewSet):
    """
    Вьюсет тегов
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ModelViewSet):
    """
    Вьюсет ингредиентов
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngridientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class UsersViewSet(UserViewSet):
    """Вьюсет пользователя"""
    @action(['get'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        """
        Демонстрация текущего пользователя
        """
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        """"
        Функция своих подписчиков
        """
        subscriptions_list = self.paginate_queryset(
            User.objects.filter(following__user=request.user)
        )
        serializer = FollowSerializer(
            subscriptions_list, many=True, context={
                'request': request
            }
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id):
        """
        Функция подписки и отписки
        """
        if request.method != 'POST':
            subscription = get_object_or_404(
                Follow,
                author=get_object_or_404(User, id=id),
                user=request.user
            )
            self.perform_destroy(subscription)
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = FollowSerializer(data={
            'user': request.user.id,
            'author': get_object_or_404(User, id=id).id
        },
            context={'request': request}
        )
        serializer.is_validate(raise_exeption=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class RecipeViewSet(ModelViewSet):
    """
    Вьюсет рецептов
    """
    queryset=Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    filter_backends = DjangoFilterBackend
    pagination_class = RecipePagination
    filter_class = RecipeFilter
    permission_classes = (
        IsAdminOrAuthorOrReadOnlyPermission, IsAuthenticatedOrReadOnly
    )
    def choice_serializer_class(self):
        """
        Выбор сериализатора в зависимости от запроса
        """
        if self.request.method in SAFE_METHODS:
            return GetRecipeSerializer
        return CreateRecipeSerializer
       
    @staticmethod
    def post_method_for_actions(request, pk, serializers):
        """
        Post запрос для создания рецепта
        """
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @staticmethod
    def delete_method_for_actions(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model_instance = get_object_or_404(model, user=user, recipe=recipe)
        model_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk):
        return self.post_method_for_actions(
            request, pk, serializers=ShopingcartSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
            return self.delete_method_for_actions(
                request=request, pk=pk, model=ShoppingCart)

    @action(detail=False, methods=['get'], permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
            return download_shopping_cart(request)
    
    @action(detail=True, methods=['post'])
    def favorite(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=FavoritedSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=Favorite)