from django.urls import re_path
from . import views

app_name = 'celery_progress'
urlpatterns = [
    re_path(r'^(?P<task_id>[\w-]+)/$', views.get_progress, name='task_status')
]
