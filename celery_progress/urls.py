from django.urls import repath
from . import views

app_name = 'celery_progress'
urlpatterns = [
    repath(r'^(?P<task_id>[\w-]+)/$', views.get_progress, name='task_status')
]
