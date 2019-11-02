from django.conf.urls import url

from celery_progress.websockets import consumers

urlpatterns = [
    url(r'^ws/progress/(?P<task_id>[\w-]+)/?$', consumers.ProgressConsumer),
]
