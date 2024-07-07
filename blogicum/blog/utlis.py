from django.core.paginator import Paginator

from .models import Post


def posts_paginator(request):
    posts = Post.objects.order_by('-pub_date').select_related('author')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
