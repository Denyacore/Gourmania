# from django.contrib import admin
# from django.urls import include, path

# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("api/", include("api.urls"), name="api"),
# ]

from django.urls import include, path

app_name = 'api'

urlpatterns = [path('v1/', include('api.urls'))]