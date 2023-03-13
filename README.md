АДРЕСС ДЛЯ ПРОВЕРКИ НА РЕВЬЮ - http://158.160.27.190/
Тестовые данные админки: email: Login:gam@mail.ru  Pass: admin
# Foodgram project
### Описание
Сервис «Продуктовый помощник»: приложение, в котором можно публиковать рецепты, добавлять чужие рецепты в список «Избранное» и подписываться на публикации других авторов, а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Для выполнения проекта вместе с техническим заданием мне был предоставлен фронтенд на React и спецификация на API.


### Стек технологий, использованный в проекте:
- Python 3.7
- Django 3.2.16
- DRF
- Docker
- Nginx
- Gunicorn
- PostgreSQL

### Запуск на удаленном сервере:
#### Клонирование репозитория

```bash
https://github.com/dimalright/foodgram-project-react.git
```

#### Установка на сервере Docker, Docker Compose
```bash
sudo apt install curl                                   # установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      # скачать скрипт для установки
sh get-docker.sh                                        # запуск скрипта
sudo apt-get install docker-compose-plugin              # последняя версия docker compose
```
#### Скопировать на сервер файлы docker-compose.yml, nginx.conf из папки infra
```bash
scp docker-compose.yml nginx.conf username@IP:/home/username/   # username - имя пользователя на сервере
                                                                # IP - публичный IP сервера
```

#### Создать и запустить контейнеры Docker, выполнить команду на сервере
```bash
sudo docker-compose up -d
```
#### Выполнить миграции, создать суперпользователя и собрать статику
```bash
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --noinput
```
#### Через админку импортировать ингредиенты из
```bash
data/ingredients.json
```
#### После запуска проект будут доступен по адресу: http://"Your_IP"/recipes/


### Запуск проекта на локальной машине:
#### Клонирование репозитория

```bash
https://github.com/StasKrut/foodgram-project-react.git
```
#### В директории infra создать фаил .env и заполнить своими данными:
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='секретный ключ Django'
```
#### Создать и запустить контейнеры Docker, как указано выше.

#### После запуска проект будут доступен по адресу: http://localhost/

#### Документация будет доступна по адресу: http://localhost/api/docs/
  
Проект сделан в рамках учебного процесса по специализации Python-разработчик (backend) Яндекс.Практикум.

Автор в рамках учебного курса ЯП Python - разработчик:
- :white_check_mark: [Dmitry Lifanov](https://github.com/dimalright)