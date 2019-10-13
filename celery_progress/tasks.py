from asgiref.sync import async_to_sync
from celery.signals import task_postrun
from channels.layers import get_channel_layer

from celery_progress.backend import Progress


@task_postrun.connect
def task_postrun_handler(task_id, **kwargs):
    """Runs after a task has finished. This will be used to push a websocket update for completed events."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        task_id,
        {'type': 'update_task_progress', 'data': {**Progress(task_id).get_info()}}
    )
