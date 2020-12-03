import json
from django.http import HttpResponse
from celery.result import AsyncResult
from celery_progress.backend import Progress
from django.views.decorators.cache import never_cache

@never_cache
def get_progress(request, task_id):
    progress = Progress(AsyncResult(task_id))
    return HttpResponse(json.dumps(progress.get_info()), content_type='application/json')
