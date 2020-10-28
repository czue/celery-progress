from celery.signals import task_postrun


@task_postrun.connect(retry=True)
def task_postrun_handler(**kwargs):
    """Runs after a task has finished. This will update the result backend to include the IGNORED result state.

    Necessary for HTTP to properly receive ignored task event."""
    if kwargs.pop('state') == 'IGNORED':
        task = kwargs.pop('task')
        task.update_state(state='IGNORED', meta=str(kwargs.pop('retval')))
