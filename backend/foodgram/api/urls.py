from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (TagViewset,UsersViewSet,RecipeViewSet,IngredientViewset)

router = DefaultRouter()

router.register(r'tags', TagViewset,basename='tags')
router.register(r'users', UsersViewSet,basename='users')
router.register(r'recipes', RecipeViewSet,basename='recipes')
router.register(r'ingredients', IngredientViewset,basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
