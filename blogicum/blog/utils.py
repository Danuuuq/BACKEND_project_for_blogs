from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic.detail import SingleObjectMixin

from .forms import CommentForm
from .models import Comment, Post


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
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        if self.object == self.request.user:
            return self.object.posts.comment_count().order_by('-pub_date')
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
        raise Http404('Данная публикация не найдена')
