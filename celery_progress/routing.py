from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/progress/(?P<task_id>[\w-]+)/$', consumers.ProgressConsumer),
]
