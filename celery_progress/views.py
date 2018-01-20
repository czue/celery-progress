import json
from django.http import HttpResponse
from celery_progress.backend import Progress


def get_progress(request, task_id):
    progress = Progress(task_id)
    return HttpResponse(json.dumps(progress.get_info()), content_type='application/json')
