from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.views.generic.edit import CreateView
from django.conf.urls.static import static
from django.urls import include, path, reverse_lazy
from django.conf import settings

urlpatterns = [
    path('profile/', include('django.contrib.auth.urls')),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
    path(
        'auth/password_change/',
        PasswordChangeView.as_view(
            form_class=PasswordChangeForm,
        ),
        name='password_change'
    )
]

handler403 = 'pages.views.access_denied'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
