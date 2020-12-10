from django.contrib import admin
from django.urls import path, include
from analytics import views_api, views

api = ([
    path('getdata', views_api.get_data, name='getdata'),
], 'api')

urlpatterns = [
    path('api/', include(api, namespace='api')),
    path('map', views.index, name='map'),
]