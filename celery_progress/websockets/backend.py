from celery_progress.backend import ProgressRecorder

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
    def push_update(task_id, data):
        try:
            async_to_sync(channel_layer.group_send)(
                task_id,
                {'type': 'update_task_progress', 'data': data}
            )
        except AttributeError:  # No channel layer to send to, so ignore it
            pass

    def set_progress(self, current, total, description=""):
        progress = super().set_progress(current, total, description)
        data = {'complete': False, 'success': None, 'progress': progress}
        self.push_update(self.task.request.id, data)

    def stop_task(self, current, total, exc):
        progress = super().stop_task(current, total, exc)
        progress.pop('exc_type')
        result = progress.pop('exc_message')
        data = {'complete': True, 'success': False, 'progress': progress, 'result': result}
        self.push_update(self.task.request.id, data)
