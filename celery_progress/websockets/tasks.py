from celery.signals import task_postrun, task_revoked

from .backend import WebSocketProgressRecorder
from celery_progress.backend import KnownResult, Progress


@task_postrun.connect(retry=True)
def task_postrun_handler(task_id, **kwargs):
    """Runs after a task has finished. This will be used to push a websocket update for completed events.

    If the websockets version of this package is not installed, this will fail silently."""
    result = KnownResult(task_id, kwargs.pop('retval'), kwargs.pop('state'))
    data = Progress(result).get_info()
    WebSocketProgressRecorder.push_update(task_id, data=data, final=True)


@task_revoked.connect(retry=True)
def task_revoked_handler(request, **kwargs):
    """Runs if a task has been revoked. This will be used to push a websocket update for revoked events.

    If the websockets version of this package is not installed, this will fail silently."""
    _result = ('terminated' if kwargs.pop('terminated') else None) or ('expired' if kwargs.pop('expired') else None) \
        or 'revoked'
    result = KnownResult(request.id, _result, 'REVOKED')
    data = Progress(result).get_info()
    WebSocketProgressRecorder.push_update(request.id, data=data, final=True)
