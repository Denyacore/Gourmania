# Foodgram by [Denyacore](https://github.com/Denyacore) & [Dimalright](https://github.com/Dimalright)



Cайт [Foodgram](http://51.250.16.52/), «Продуктовый помощник».Онлайн-сервис с API. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
## Использованные технологии

![Python](https://img.shields.io/badge/Python-3.7-3776AB?logo=Python&style=flat-square)


[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)

[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)

[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)

[![Docker Compose](https://img.shields.io/badge/Docker_Compose-464646?style=flat-square)](https://docs.docker.com/compose/)


[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)

[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)

[![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)



## Запуск
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Denyacore/foodgram-project-react
```
```
cd infra
```

Для функционирования - создать файл .env и прописать переменные окружения в нём.

```bash
SECRET_KEY= <ваш_secret_key>
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=password # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```

Выполнить команду из директории infra, где находится файл docker-compose.yaml
```bash
docker-compose up
```
Выполнить миграции, создать суперпользователя и собрать статику. 
```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
```
Заполнить базу данными
```
docker-compose exec web python manage.py loaddata fixtures.json
```

После этого станут доступны учетные записи 

| role  | email             | password     |
|-------|-------------------|--------------|
| admin | a@a.com           | admin        |
| user  | leha@leha.com     | leha123456   |
| user  | julya@julya.com   | julya123456  |
| user  | gordon@gordon.com | gordon123456 |

## Примеры запросов:

API работает на :  http://51.250.16.52/api/


### Регистрация нового пользователя:

```bash
POST - 'http://51.250.16.52/api/users/'
```
```yaml
{
  "username": "user_username.",
  "email": "user@mail.ru",
  "password": "user_password.",
  "first_name": "user_first_name",
  "last_name": "user_last_name"
}
```

#### Ответ
```yaml
{
  "id": 2,
  "username": "user_username.",
  "email": "user@mail.ru",
  "first_name": "user_first_name",
  "last_name": "user_last_name"
}
```

### Получение токена:
#### Запрос
```bash
POST - 'http://51.250.16.52/api/auth/token/login/'
```
```yaml
{
  "password": "user_password.",
  "email": "user@mail.ru"
}
```

#### Ответ
```yaml
{ "auth_token": "token_value" }
```

### Информация о своей учетной записи:
#### Запрос
```bash
GET - 'http://51.250.16.52/api/users/me/'
header 'Authorization: Token "token_value"'
```

#### Ответ
```yaml
{
  "id": 2,
  "username": "user_username.",
  "email": "user@mail.ru",
  "first_name": "user_first_name",
  "last_name": "user_last_name",
  "is_subscribed": false
}
```

### Добавление нового рецепта:
#### Запрос
```bash
POST - 'http://51.250.16.52/api/recipes/'
header 'Authorization: Token "token_value"'
```
```yaml
{
  "ingredients": [
    {
      "id": 11,
      "amount": 270
    },
    {
      "id": 38,
      "amount": 2
    },
    {
      "id": 267,
      "amount": 30
    },
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "Название рецепта",
  "text": "Описание рецепта",
  "cooking_time": 15
}
```

#### Ответ
```yaml
{
  "id": 4,
  "tags": [
    {
      "id": 1,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    },
    {
      "id": 2,
      "name": "Обед",
      "color": "#0000CD",
      "slug": "dinner"
    }
  ],
  "author": {
    "id": 2,
    "username": "user_username.",
    "email": "user@mail.ru",
    "first_name": "user_first_name",
    "last_name": "user_last_name",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 11,
      "name": "Вода",
      "measurement_unit": "мл",
      "amount": 270
    },
    {
      "id": 38,
      "name": "Сахар",
      "measurement_unit": "ч. ложка",
      "amount": 2
    },
    {
      "id": 267,
      "name": "Молоко",
      "measurement_unit": "мл",
      "amount": 30
    }
  ],
  "is_favorited": false,
  "is_in_shopping_cart": false,
  "name": "Название рецепта",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "Описание рецепта.",
  "cooking_time": 15
}
```
