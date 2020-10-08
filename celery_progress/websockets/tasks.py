from celery.signals import task_postrun

from .backend import WebSocketProgressRecorder
from celery_progress.backend import KnownResult, Progress


@task_postrun.connect(retry=True)
def task_postrun_handler(task_id, **kwargs):
    """Runs after a task has finished. This will be used to push a websocket update for completed events.

    If the websockets version of this package is not installed, this will fail silently."""
    result = KnownResult(task_id, kwargs.pop('retval'), kwargs.pop('state'))
    data = Progress(result).get_info()
    WebSocketProgressRecorder.push_update(task_id, data=data, final=True)
