from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User
from .utils import (
    BaseClassComment, AddPostsUserAndCategoryView,
    OnlyAuthorMixin, PermissionUnpublishedMixin
)


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
    paginate_by = settings.POSTS_PER_PAGE


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
