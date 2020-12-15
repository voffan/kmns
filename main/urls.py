from django.urls import path, include
from main import views, views_api

api = ([
    path('save', views_api.table_save, name='save'),
    path('gettable/<int:table_id>', views_api.get_table, name='gettable'),
    path('delete/<int:table_id>', views_api.delete_table, name='deletetable'),
    path('addfield/<int:table_id>>',views_api.add_field, name='addfield'),
    path('deletefield/<int:field_id>',views_api.delete_field, name='deletefield'),
    path('savefields/<int:table_id>',views_api.save_fields, name='savefields'),
    path('addrow/<int:table_id>', views_api.add_row, name='addrow'),
    path('deleterow/<int:row_id>', views_api.delete_row, name='deleterow'),
    path('saverow', views_api.save_row, name='saverow'),
    path('gettabledata', views_api.get_table_data, name='gettabledata'),
], 'api')

urlpatterns = [
    path('start', views.start, name='start'),
    path('list/', views.tables_list, name='list'),
    path('indicators/', views.indicators, name='indicators'),
    path('exportindicators/', views.export_indicators, name='exportindicators'),
    path('exporttable/<int:table_id>', views.export_table, name='exporttable'),
    path('<int:table_id>', views.table_data, name='table_data'),
    path('fields/<int:table_id>', views.table_fields, name='table_fields'),
    path('admin', views.admins, name='admin_page'),
    path('api/', include(api, namespace='api')),
]