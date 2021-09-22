from django.urls import path

from task4.views import hw, view, ShowNumbersView

urlpatterns = [
    path("hw/", hw),
    path("task4/", view),
    path("info/", ShowNumbersView.as_view())
]