from django.contrib.auth.mixins import (
    UserPassesTestMixin, LoginRequiredMixin, PermissionRequiredMixin
)
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.core.paginator import Paginator
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Post, Category, User, Comment
from .forms import CommentForm, PostForm, UserForm
from django.utils import timezone
from datetime import datetime


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PermissionUnpublishedMixin(UserPassesTestMixin):

    def test_func(self) -> bool | None:
        object = self.get_object()
        if not object.is_published or object.pub_date >= timezone.now() or not object.category.is_published:
            return object.author == self.request.user
        if object.pub_date >= timezone.now():
            return object.author == self.request.user
        else:
            return True

    def handle_no_permission(self) -> HttpResponseRedirect:
        raise Http404


class AuthorAndLoginMixit(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self) -> HttpResponseRedirect:
        return redirect('blog:post_detail', pk=self.kwargs['pk'])


class PostsUserView(SingleObjectMixin, ListView):
    template_name = 'blog/profile.html'
    slug_field = 'username'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=User.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.object
        return context

    def get_queryset(self):
        if self.object == self.request.user:
            return self.object.posts.comment_count().order_by('-pub_date')
        else:
            return self.object.posts(
                manager='published'
            ).all().order_by('-pub_date')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'slug': self.request.user}
        )


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = 10
    queryset = Post.published.all()


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'slug': self.object.author.username}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(AuthorAndLoginMixit, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.kwargs['pk'])
        context['form'] = PostForm(instance=instance)
        # breakpoint()
        return context

    def form_valid(self, form):
        return super().form_valid(form)


class PostDetailView(PermissionUnpublishedMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    publication = None
    template_name = 'blog/comment.html'
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.publication = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.publication = self.publication
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.publication.pk})


class CommentUpdateView(OnlyAuthorMixin, LoginRequiredMixin, UpdateView):
    publication = None
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.publication = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.publication = self.publication
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.publication.pk})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['post_id']})


class PostsCategoryView(SingleObjectMixin, ListView):
    template_name = 'blog/category.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Category.objects.filter(is_published=True))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.object
        return context

    def get_queryset(self):
        return self.object.posts(
            manager='published'
        ).all().order_by('-pub_date')
