from abc import ABCMeta, abstractmethod
from celery.result import AsyncResult
from decimal import Decimal


PROGRESS_STATE = 'PROGRESS'


class AbtractProgressRecorder(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_progress(self, current, total):
        pass


class ConsoleProgressRecorder(AbtractProgressRecorder):

    def set_progress(self, current, total):
        print('processed {} items of {}'.format(current, total))


class ProgressRecorder(AbtractProgressRecorder):

    def __init__(self, task):
        self.task = task

    def set_progress(self, current, total):
        percent = round((Decimal(current) / Decimal(total)) * Decimal(100), 2) if total > 0 else 0
        self.task.update_state(
            state=PROGRESS_STATE,
            meta={
                'current': current,
                'total': total,
                'percent': percent,
            }
        )


class Progress(object):

    def __init__(self, task_id):
        self.task_id = task_id
        self.result = AsyncResult(task_id)

    def get_info(self):
        if self.result.ready():
            return {
                'complete': True,
                'success': self.result.successful(),
                'progress': _get_completed_progress()
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
    {
        'current': 0,
        'total': 100,
        'percent': 0,
    }


