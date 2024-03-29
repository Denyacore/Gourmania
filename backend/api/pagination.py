from rest_framework.pagination import PageNumberPagination


class RecipePagination(PageNumberPagination):
    """
    Пагинация с ограничением объектов на странице
    """
    page_size_query_param = 'limit'
    page_size = 6
