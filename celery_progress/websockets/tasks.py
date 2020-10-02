from celery.signals import task_postrun

from .backend import WebSocketProgressRecorder


@task_postrun.connect(retry=True)
def task_postrun_handler(task_id, **kwargs):
    """Runs after a task has finished. This will be used to push a websocket update for completed events.

    If the websockets version of this package is not installed, this will fail silently."""
    data = {
        'complete': True,
        'success': kwargs.pop('state') == 'SUCCESS',
        'progress': {'pending': False, 'current': 100, 'total': 100, 'percent': 100},
        'result': str(kwargs.pop('retval'))
    }
    WebSocketProgressRecorder.push_update(task_id, data=data)
