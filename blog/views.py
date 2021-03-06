from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from rest_framework import generics
from taggit.models import Tag
from users.models import Profile

from .models import Post
from .serializers import PostSerializer


# =============================================================================
# REST
# =============================================================================


# from rest_framework.renderers import TemplateHTMLRenderer
# from rest_framework.response import Response

class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all().order_by('-date_posted')
    page_size = 5


class UserPostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    page_size = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(author=user).order_by('-date_posted')


# =============================================================================
# Main part of the site
# =============================================================================

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model?_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        return context


class UserPostListView(ListView):
    model = Post
    template_name = 'users/profile_posts.html'  # <app>/<model?_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context = super(UserPostListView, self).get_context_data(**kwargs)
        context['user'] = user
        context['tags'] = Tag.objects.all()
        context['follower_count'] = Profile.objects.get(user=user).get_followers().count()
        context['following_count'] = Profile.objects.get(user=user).get_following().count()
        return context


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        return context


#    template_name = 'blog/post_detail.html'

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'tags', 'content', 'image']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'tags', 'content', 'image']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        else:
            return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        else:
            return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

# Create your views here.
