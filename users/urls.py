from django.contrib import admin
from django.urls import path, include
from users import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile', views.user_profile, name='profile'),
    path('changepassword', views.change_password, name='changepassword'),
]