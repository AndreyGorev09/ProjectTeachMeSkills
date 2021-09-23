from django.urls import path
from django.contrib import admin

from blog.views import AllPostView, SinglePostView, SingleDeleteView, SingleCreateView, SingleUpdateView

urlpatterns = [
    path("", AllPostView.as_view()),
    path("<int:pk>/", SinglePostView.as_view()),
    path("<int:pk>/delete/", SingleDeleteView.as_view()),
    path("create/", SingleCreateView.as_view()),
    path("<int:pk>/update/", SingleUpdateView.as_view()),
]