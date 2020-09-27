from django.urls import path, include
from reports import views, views_api

api = ([
    path('deletereport/<int:report_id>', views_api.delete_report, name='deletereport'),
    path('getreport/<int:report_id>', views_api.get_report, name='getreport'),
    path('savereport', views_api.save_reports, name='savereport'),
], 'api')

urlpatterns = [
    path('list/', views.reports_list, name='list'),
    path('<int:report_id>', views.report_data, name='report_tables'),
    path('api/', include(api, namespace='api')),
]