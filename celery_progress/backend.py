from abc import ABCMeta, abstractmethod
from decimal import Decimal

from celery.result import EagerResult, allow_join_result
from celery.backends.base import DisabledBackend


PROGRESS_STATE = 'PROGRESS'


class AbstractProgressRecorder(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_progress(self, current, total, description=""):
        pass

    @abstractmethod
    def stop_task(self, current, total, exc):
        pass


class ConsoleProgressRecorder(AbstractProgressRecorder):

    def set_progress(self, current, total, description=""):
        print('processed {} items of {}. {}'.format(current, total, description))

    def stop_task(self, current, total, exc):
        pass


class ProgressRecorder(AbstractProgressRecorder):

    def __init__(self, task):
        self.task = task

    def set_progress(self, current, total, description=""):
        percent = 0
        if total > 0:
            percent = (Decimal(current) / Decimal(total)) * Decimal(100)
            percent = float(round(percent, 2))
        state = PROGRESS_STATE
        meta = {
            'pending': False,
            'current': current,
            'total': total,
            'percent': percent,
            'description': description
        }
        self.task.update_state(
            state=state,
            meta=meta
        )
        return state, meta

    def stop_task(self, current, total, exc):
        state = 'FAILURE'
        meta = {
            'pending': False,
            'current': current,
            'total': total,
            'percent': 100.0,
            'exc_message': str(exc),
            'exc_type': str(type(exc))
        }
        self.task.update_state(
            state=state,
            meta=meta
        )
        return state, meta


class Progress(object):

    def __init__(self, result):
        """
        result:
            an AsyncResult or an object that mimics it to a degree
        """
        self.result = result

    def get_info(self):
        if self.result.ready():
            success = self.result.successful()
            with allow_join_result():
                return {
                    'complete': True,
                    'success': success,
                    'progress': _get_completed_progress(),
                    'result': self.result.get(self.result.id) if success else str(self.result.info),
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
                'progress': _get_unknown_progress(self.result.state),
            }
        else:
            return {
                'complete': True,
                'success': False,
                'progress': _get_unknown_progress(self.result.state),
                'result': 'Unknown state {}'.format(str(self.result.info)),
            }


class KnownResult(EagerResult):
    """Like EagerResult but supports non-ready states."""
    def __init__(self, id, ret_value, state, traceback=None):
        """
        ret_value:
            result, exception, or progress metadata
        """
        # set backend to get state groups (like READY_STATES in ready())
        self.backend = DisabledBackend
        super().__init__(id, ret_value, state, traceback)

    def ready(self):
        return super(EagerResult, self).ready()

    def __del__(self):
        # throws an exception if not overridden
        pass


def _get_completed_progress():
    return {
        'pending': False,
        'current': 100,
        'total': 100,
        'percent': 100,
    }


def _get_unknown_progress(state):
    return {
        'pending': state == 'PENDING',
        'current': 0,
        'total': 100,
        'percent': 0,
    }
