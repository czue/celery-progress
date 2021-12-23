# Celery Progress Bars for Django

Drop in, dependency-free progress bars for your Django/Celery applications.

Super simple setup. Lots of customization available.

## Demo

[Celery Progress Bar demo on Build With Django](https://buildwithdjango.com/projects/celery-progress/)

### Github demo application: build a download progress bar for Django
Starting with Celery can be challenging, [eeintech](https://github.com/eeintech) built a complete [Django demo application](https://github.com/eeintech/django-celery-progress-demo) along with a [step-by-step guide](https://eeinte.ch/stream/progress-bar-django-using-celery/) to get you started on building your own progress bar!

## Installation

If you haven't already, make sure you have properly [set up celery in your project](https://docs.celeryproject.org/en/stable/getting-started/first-steps-with-celery.html#first-steps).

Then install this library:

```bash
pip install celery-progress
```

## Usage

### Prerequisites

First add `celery_progress` to your `INSTALLED_APPS` in `settings.py`.

Then add the following url config to your main `urls.py`:

```python
from django.urls import re_path, include
re_path(r'^celery-progress/', include('celery_progress.urls')),  # the endpoint is configurable
```

### Recording Progress

In your task you should add something like this:

```python
from celery import shared_task
from celery_progress.backend import ProgressRecorder
import time

@shared_task(bind=True)
def my_task(self, seconds):
    progress_recorder = ProgressRecorder(self)
    result = 0
    for i in range(seconds):
        time.sleep(1)
        result += i
        progress_recorder.set_progress(i + 1, seconds)
    return result
```

You can add an optional progress description like this:

```python
  progress_recorder.set_progress(i + 1, seconds, description='my progress description')
```

### Displaying progress

In the view where you call the task you need to get the task ID like so:

**views.py**
```python
def progress_view(request):
    result = my_task.delay(10)
    return render(request, 'display_progress.html', context={'task_id': result.task_id})
```

Then in the page you want to show the progress bar you just do the following.

#### Add the following HTML wherever you want your progress bar to appear:

**display_progress.html**
```html
<div class='progress-wrapper'>
  <div id='progress-bar' class='progress-bar' style="background-color: #68a9ef; width: 0%;">&nbsp;</div>
</div>
<div id="progress-bar-message">Waiting for progress to start...</div>
```

#### Import the javascript file.

**display_progress.html**
```html
<script src="{% static 'celery_progress/celery_progress.js' %}"></script>
```

#### Initialize the progress bar:

```javascript
// vanilla JS version
document.addEventListener("DOMContentLoaded", function () {
  var progressUrl = "{% url 'celery_progress:task_status' task_id %}";
  CeleryProgressBar.initProgressBar(progressUrl);
});
```

or

```javascript
// JQuery
$(function () {
  var progressUrl = "{% url 'celery_progress:task_status' task_id %}";
  CeleryProgressBar.initProgressBar(progressUrl)
});
```

### Displaying the result of a task

If you'd like you can also display the result of your task on the front end. 

To do that follow the steps below. Result handling can also be customized.

#### Initialize the result block:

This is all that's needed to render the result on the page.

**display_progress.html**
```html
<div id="celery-result"></div>
```

But more likely you will want to customize how the result looks, which can be done as below:

```javascript
// JQuery
var progressUrl = "{% url 'celery_progress:task_status' task_id %}";

function customResult(resultElement, result) {
  $( resultElement ).append(
    $('<p>').text('Sum of all seconds is ' + result)
  );
}

$(function () {
  CeleryProgressBar.initProgressBar(progressUrl, {
    onResult: customResult,
  })
});
```

## Customization

The `initProgressBar` function takes an optional object of options. The following options are supported:

| Option | What it does | Default Value |
|--------|--------------|---------------|
| pollInterval | How frequently to poll for progress (in milliseconds) | 500 |
| progressBarId | Override the ID used for the progress bar | 'progress-bar' |
| progressBarMessageId | Override the ID used for the progress bar message | 'progress-bar-message' |
| progressBarElement | Override the *element* used for the progress bar. If specified, progressBarId will be ignored. | document.getElementById(progressBarId) |
| progressBarMessageElement | Override the *element* used for the progress bar message. If specified, progressBarMessageId will be ignored. | document.getElementById(progressBarMessageId) |
| resultElementId | Override the ID used for the result | 'celery-result' |
| resultElement | Override the *element* used for the result. If specified, resultElementId will be ignored. | document.getElementById(resultElementId) |
| onProgress | function to call when progress is updated | onProgressDefault |
| onSuccess | function to call when progress successfully completes | onSuccessDefault |
| onError | function to call on a known error with no specified handler | onErrorDefault |
| onRetry | function to call when a task attempts to retry | onRetryDefault |
| onIgnored | function to call when a task result is ignored | onIgnoredDefault |
| onTaskError | function to call when progress completes with an error | onError |
| onNetworkError | function to call on a network error (ignored by WebSocket) | onError |
| onHttpError | function to call on a non-200 response (ignored by WebSocket) | onError |
| onDataError | function to call on a response that's not JSON or has invalid schema due to a programming error | onError |
| onResult | function to call when returned non empty result | CeleryProgressBar.onResultDefault |
| barColors | dictionary containing color values for various progress bar states. Colors that are not specified will defer to defaults | barColorsDefault |
| defaultMessages | dictionary containing default messages that can be overridden | see below |

The `barColors` option allows you to customize the color of each progress bar state by passing a dictionary of key-value pairs of `state: #hexcode`. The defaults are shown below.

| State | Hex Code | Image Color | 
|-------|----------|:-------------:|
| success | #76ce60 | ![#76ce60](https://via.placeholder.com/15/76ce60/000000?text=+) |
| error | #dc4f63 | ![#dc4f63](https://via.placeholder.com/15/dc4f63/000000?text=+) |
| progress | #68a9ef | ![#68a9ef](https://via.placeholder.com/15/68a9ef/000000?text=+) |
| ignored | #7a7a7a | ![#7a7a7a](https://via.placeholder.com/15/7a7a7a/000000?text=+) |

The `defaultMessages` option allows you to override some default messages in the UI. At the moment these are:

| Message Id | When Shown | Default Value |
|-------|----------|:-------------:|
| waiting | Task is waiting to start | 'Waiting for task to start...'
| started | Task has started but reports no progress | 'Task started...'

# WebSocket Support

Additionally, this library offers WebSocket support using [Django Channels](https://channels.readthedocs.io/en/latest/)
courtesy of [EJH2](https://github.com/EJH2/).

A working example project leveraging WebSockets is [available here](https://github.com/EJH2/cp_ws-example).

To use WebSockets, install with `pip install celery-progress[websockets,redis]` or
`pip install celery-progress[websockets,rabbitmq]` (depending on broker dependencies).

See `WebSocketProgressRecorder` and `websockets.js` for details.

# Securing the get_progress endpoint
By default, anyone can see the status and result of any task by accessing `/celery-progress/<task_id>`

To limit access, you need to wrap `get_progress()` in a view of your own which implements the permissions check, and create a new url routing to point to your view.  Make sure to remove any existing (unprotected) celery progress urls from your root urlconf at the same time.


For example, requiring login with a class-based view:
```python

# views.py
from celery_progress.views import get_progress
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View

class TaskStatus(LoginRequiredMixin, View):
    def get(self, request, task_id, *args, **kwargs):
        # Other checks could go here
        return get_progress(request, task_id=task_id)
```

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    ...
    path('task-status/<uuid:task_id>', views.TaskStatus.as_view(), name='task_status'),
    ...
]
```

Requiring login with a function-based view:
```python

# views.py
from celery_progress.views import get_progress
from django.contrib.auth.decorators import login_required

@login_required
def task_status(request, task_id):
    # Other checks could go here
    return get_progress(request, task_id)
```

```python
# urls.py
from django.urls import path

from . import views

urlpatterns = [
    ...
    path('task-status/<uuid:task_id>', views.task_status, name='task_status'),
    ...
]
```


Any links to `'celery_progress:task_status'` will need to be changed to point to your new endpoint.

