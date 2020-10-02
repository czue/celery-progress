from celery_progress.backend import ProgressRecorder, Progress

try:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
except ImportError:
    channel_layer = None
else:
    channel_layer = get_channel_layer()

if not channel_layer:
    RuntimeError(
        'Tried to use websocket progress bar, but dependencies were not installed / configured. '
        'Use pip install celery-progress[websockets] and set up channels to enable this feature. '
        'See: https://channels.readthedocs.io/en/latest/ for more details.'
    )


class WebSocketProgressRecorder(ProgressRecorder):

    @staticmethod
    def push_update(task_id):
        try:
            async_to_sync(channel_layer.group_send)(
                task_id,
                {'type': 'update_task_progress', 'data': {**Progress(task_id).get_info()}}
            )
        except AttributeError:  # No channel layer to send to, so ignore it
            pass

    def set_progress(self, current, total, description=""):
        super().set_progress(current, total, description)
        self.push_update(self.task.request.id)

    def stop_task(self, current, total, exc):
        super().stop_task(current, total, exc)
        self.push_update(self.task.request.id)
