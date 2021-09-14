from django.http import HttpRequest
from django.http import HttpResponse

from django.contrib import admin
from django.urls import path, include




def hello_world(request: HttpRequest):
    return HttpResponse("Hello world")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('hw/', hello_world),
    path('task4/', include("task4.urls")),
]
