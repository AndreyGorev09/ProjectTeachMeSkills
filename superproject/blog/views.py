from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView

from blog.models import Post


class AllPostView(ListView):
    model = Post


class SinglePostView(DetailView):
    model = Post


class SingleDeleteView(DeleteView):
    template_name = "blog/delete.html"
    model = Post
    success_url = "/blog/"


class SingleCreateView(CreateView):
    model = Post
    fields = ["title", "content", "hidden"]


class SingleUpdateView(UpdateView):
    model = Post
    fields = ["title", "content", "hidden"]



