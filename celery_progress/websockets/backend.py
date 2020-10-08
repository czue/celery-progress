import logging

from celery_progress.backend import ProgressRecorder, Progress, KnownResult

try:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
except ImportError:
    channel_layer = None
else:
    channel_layer = get_channel_layer()

logger = logging.getLogger(__name__)


class WebSocketProgressRecorder(ProgressRecorder):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not channel_layer:
            logger.warning(
                'Tried to use websocket progress bar, but dependencies were not installed / configured. '
                'Use pip install celery-progress[websockets] and set up channels to enable this feature. '
                'See: https://channels.readthedocs.io/en/latest/ for more details.'
            )

    @staticmethod
    def push_update(task_id, data, final=False):
        try:
            async_to_sync(channel_layer.group_send)(
                task_id,
                {'type': 'update_task_progress', 'data': data}
            )
        except AttributeError:  # No channel layer to send to, so ignore it
            pass
        except RuntimeError as e:  # We're sending messages too fast for asgiref to handle, drop it
            if final and channel_layer:  # Send error back to post-run handler for a retry
                raise e

    def set_progress(self, current, total, description=""):
        state, meta = super().set_progress(current, total, description)
        result = KnownResult(self.task.request.id, meta, state)
        data = Progress(result).get_info()
        self.push_update(self.task.request.id, data)

    def stop_task(self, current, total, exc):
        state, _ = super().stop_task(current, total, exc)
        result = KnownResult(self.task.request.id, exc, state)
        data = Progress(result).get_info()
        self.push_update(self.task.request.id, data)
