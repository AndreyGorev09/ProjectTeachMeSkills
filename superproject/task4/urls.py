from django.urls import path

from .views import index
from .views import task

urlpatterns = [
    path("", task),
    path("check/", index),
]