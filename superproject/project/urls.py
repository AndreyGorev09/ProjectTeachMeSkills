from django.contrib import admin
from django.urls import path

from task4.views import hello_world, view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('hw/', hello_world),
    path("task4/", view)
]
