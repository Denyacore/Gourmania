from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    """
    Модель пользователя с выборкой ролей
    """

    USER = "user"
    ADMIN = "admin"
    ROLES = (
        (USER, "user"),
        (ADMIN, "admin"),
    )
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(max_length=150, unique=True, validators=[
                                username_validator], verbose_name="Логин")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    role = models.CharField(max_length=30, choices=ROLES,
                            default=USER, verbose_name="Роль")
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        ordering = ("id",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [models.CheckConstraint(check=~models.Q(
            username__iexact="me"), name="username_is_not_me")]

    def __str__(self):
        return self.username


class Follow(models.Model):
    """
    Модель подписки на авторов
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Блогер")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_follow"),
        ]
