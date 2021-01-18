from django.contrib import admin
from django.urls import path, include
from imports import views

urlpatterns = [
    path('importfile/', views.import_files, name='importfile'),
    path('importresult/<int:result_id>', views.ImportResultDetailView.as_view(), name='importresult'),
]