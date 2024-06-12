import json
from django.http import HttpResponse
from celery.result import AsyncResult, GroupResult
from celery_progress.backend import Progress, GroupProgress
from django.views.decorators.cache import never_cache

@never_cache
def get_progress(request, task_id):
    progress = Progress(AsyncResult(task_id))
    return HttpResponse(json.dumps(progress.get_info()), content_type='application/json')



@never_cache
def get_group_progress(request, group_id):
    group_progress = GroupProgress(GroupResult.restore(group_id))
    return HttpResponse(json.dumps(group_progress.get_info()), content_type='application/json')
