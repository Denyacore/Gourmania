from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Панель админа для редактирования пользователей
    """

    list_display = ("role", "username", "email", "first_name", "last_name")
    list_display_links = ("username",)
    search_fields = (
        "role",
        "username",
    )
    list_filter = (
        "username",
        "email",
    )
    empty_value_display = "-пусто-"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """
    Панель админа для редактирования подписок на авторов
    """

    list_display = (
        "user",
        "author",
    )
    list_display_links = ("user",)
    search_fields = (
        "user",
        "author",
    )
    list_filter = ("user",)
    empty_value_display = "-пусто-"
