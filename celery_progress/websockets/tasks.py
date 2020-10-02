from celery.signals import task_postrun

from .backend import channel_layer, WebSocketProgressRecorder


@task_postrun.connect
def task_postrun_handler(task_id, **kwargs):
    """Runs after a task has finished. This will be used to push a websocket update for completed events.

    If the websockets version of this package is not installed, this will do nothing."""
    if channel_layer:
        WebSocketProgressRecorder.push_update(task_id)
