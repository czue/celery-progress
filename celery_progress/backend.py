import logging
from abc import ABCMeta, abstractmethod
from decimal import Decimal

from celery.result import AsyncResult, allow_join_result

try:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
except ImportError:
    async_to_sync = get_channel_layer = None
    WEBSOCKETS_AVAILABLE = False
else:
    WEBSOCKETS_AVAILABLE = get_channel_layer()

PROGRESS_STATE = 'PROGRESS'


logger = logging.getLogger(__name__)


class AbstractProgressRecorder(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_progress(self, current, total):
        pass


class ConsoleProgressRecorder(AbstractProgressRecorder):

    def set_progress(self, current, total):
        print('processed {} items of {}'.format(current, total))


class ProgressRecorder(AbstractProgressRecorder):

    def __init__(self, task):
        self.task = task

    def set_progress(self, current, total, description=""):
        percent = 0
        if total > 0:
            percent = (Decimal(current) / Decimal(total)) * Decimal(100)
            percent = float(round(percent, 2))
        self.task.update_state(
            state=PROGRESS_STATE,
            meta={
                'current': current,
                'total': total,
                'percent': percent,
                'description': description
            }
        )

    def stop_task(self, current, total, exc):
        self.task.update_state(
            state='FAILURE',
            meta={
                'current': current,
                'total': total,
                'percent': 100.0,
                'exc_message': str(exc),
                'exc_type': str(type(exc))
            }
        )


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


class Progress(object):

    def __init__(self, task_id):
        self.task_id = task_id
        self.result = AsyncResult(task_id)

    def get_info(self):
        if self.result.ready():
            success = self.result.successful()
            with allow_join_result():
                return {
                    'complete': True,
                    'success': success,
                    'progress': _get_completed_progress(),
                    'result': self.result.get(self.task_id) if success else None,
                }
        elif self.result.state == PROGRESS_STATE:
            return {
                'complete': False,
                'success': None,
                'progress': self.result.info,
            }
        elif self.result.state in ['PENDING', 'STARTED']:
            return {
                'complete': False,
                'success': None,
                'progress': _get_unknown_progress(),
            }
        return self.result.info


def _get_completed_progress():
    return {
        'current': 100,
        'total': 100,
        'percent': 100,
    }


def _get_unknown_progress():
    return {
        'current': 0,
        'total': 100,
        'percent': 0,
    }
