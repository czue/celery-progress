import logging

from celery_progress.backend import ProgressRecorder, Progress

try:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
except ImportError:
    async_to_sync = get_channel_layer = None
    WEBSOCKETS_AVAILABLE = False
else:
    WEBSOCKETS_AVAILABLE = get_channel_layer()


logger = logging.getLogger(__name__)


class WebSocketProgressRecorder(ProgressRecorder):

    @staticmethod
    def push_update(task_id):
        if WEBSOCKETS_AVAILABLE:
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    task_id,
                    {'type': 'update_task_progress', 'data': {**Progress(task_id).get_info()}}
                )
            except AttributeError:  # No channel layer to send to, so ignore it
                pass
        else:
            logger.info(
                'Tried to use websocket progress bar, but dependencies were not installed / configured. '
                'Use pip install celery-progress[websockets] and setup channels to enable this feature.'
                'See: https://channels.readthedocs.io/en/latest/ for more details.'
            )

    def set_progress(self, current, total, description=""):
        super().set_progress(current, total, description)
        self.push_update(self.task.request.id)

    def stop_task(self, current, total, exc):
        super().stop_task(current, total, exc)
        self.push_update(self.task.request.id)
