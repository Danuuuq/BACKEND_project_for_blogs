from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.views.generic.detail import SingleObjectMixin

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User


class BaseClassComment(LoginRequiredMixin):
    publication = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.publication = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.publication = self.publication
        return super().form_valid(form)


class AddPostsUserAndCategoryView(SingleObjectMixin):
    paginate_by = 10

    def get_queryset(self):
        if self.object == self.request.user:
            return self.object.posts.comment_count().order_by('-pub_date')
        else:
            return self.object.posts(
                manager='published'
            ).all().order_by('-pub_date')


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PermissionUnpublishedMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        if (
            object.pub_date >= timezone.now()
            or not object.is_published
            or not object.category.is_published
        ):
            return object.author == self.request.user
        else:
            return True

    def handle_no_permission(self):
        raise Http404


class PostsUserView(AddPostsUserAndCategoryView, ListView):
    template_name = 'blog/profile.html'
    slug_field = 'username'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=User.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.object
        return context


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
    queryset = Post.published
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = 10


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


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    queryset = Post.objects.with_related_data()
    form_class = PostForm
    template_name = 'blog/create.html'

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.kwargs['pk'])


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    queryset = Post.objects.with_related_data()
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.kwargs['pk'])
        context['form'] = PostForm(instance=instance)
        return context

    def form_valid(self, form):
        return super().form_valid(form)


class PostDetailView(PermissionUnpublishedMixin, DetailView):
    queryset = Post.objects.with_related_data()
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CommentCreateView(BaseClassComment, CreateView):
    pass


class CommentUpdateView(BaseClassComment, OnlyAuthorMixin, UpdateView):
    pk_url_kwarg = 'comment_id'


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )


class PostsCategoryView(AddPostsUserAndCategoryView, ListView):
    template_name = 'blog/category.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(
            queryset=Category.objects.filter(is_published=True)
        )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.object
        return context
