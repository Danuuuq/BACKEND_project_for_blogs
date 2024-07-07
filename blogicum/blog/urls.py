from django.urls import path, include

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(), name='post_detail'),
    path('posts/create/',
         views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/edit/',
         views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(), name='delete_post'),
    path('category/<slug:slug>/',
         views.PostsCategoryView.as_view(), name='category_posts'),
    path('profile/<slug:slug>/',
         views.PostsUserView.as_view(), name='profile'),
    path('profile/edit',
         views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('posts/<int:post_id>/comment/',
         views.CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:post_id>/comment/<int:comment_id>',
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(), name='delete_comment')
]
