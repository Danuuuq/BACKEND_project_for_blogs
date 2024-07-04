from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy, reverse

from .models import Post, Category, User, Comment
from .forms import CommentForm


class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'    


class PostListView(ListView):
    model = Post
    ordering = '-pub_date'
    paginate_by = 10
    template_name = 'blog/index.html'


class PostCreateView(CreateView):
    model = Post
    fields = '__all__'
    template_name = 'blog/create.html'


class PostUpdateView(UpdateView):
    model = Post
    fields = '__all__'
    template_name = 'blog/create.html'


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/create.html'


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'


class CommentCreateView(CreateView):
    post = None
    model = Comment
    form_class = CommentForm
    
    def dispatch(self, request, *args, **kwargs):
        self.post = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valig(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('blog:detail', kwargs={'pk': self.post.pk})


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )
    posts = category.posts(manager='published').all()
    context = {
        'category': category,
        'post_list': posts}
    return render(request, template, context)
