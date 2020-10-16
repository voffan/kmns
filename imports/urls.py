from django.contrib import admin
from django.urls import path, include
from imports import views

urlpatterns = [
    path('importfiles/', views.import_files, name='importfiles'),
]