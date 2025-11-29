from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from movies.views_front import index, register, profile, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('movies.urls')),
    path('', index, name='index'),
    path('profile/', profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='movies/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
]
