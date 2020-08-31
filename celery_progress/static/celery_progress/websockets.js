var CeleryWebSocketProgressBar = (function () {
    function onSuccessDefault(progressBarElement, progressBarMessageElement, result) {
        CeleryProgressBar.onSuccessDefault(progressBarElement, progressBarMessageElement);
    }

    function onResultDefault(resultElement, result) {
        CeleryProgressBar.onResultDefault(resultElement, result);
    }

    function onErrorDefault(progressBarElement, progressBarMessageElement, excMessage, data) {
        CeleryProgressBar.onErrorDefault(progressBarElement, progressBarMessageElement, excMessage, data);
    }

    function onProgressDefault(progressBarElement, progressBarMessageElement, progress) {
        CeleryProgressBar.onProgressDefault(progressBarElement, progressBarMessageElement, progress);
    }

    function onData(data, onProgress, onSuccess, onTaskError, onDataError, onResult, progressBarElement, progressBarMessageElement, resultElement) {
        return CeleryProgressBar.onData(data, onProgress, onSuccess, onTaskError, onDataError, onResult, progressBarElement, progressBarMessageElement, resultElement);
    }

    function initProgress (progressUrl, options) {
        options = options || {};
        var progressBarId = options.progressBarId || 'progress-bar';
        var progressBarMessage = options.progressBarMessageId || 'progress-bar-message';
        var progressBarElement = options.progressBarElement || document.getElementById(progressBarId);
        var progressBarMessageElement = options.progressBarMessageElement || document.getElementById(progressBarMessage);
        var onProgress = options.onProgress || onProgressDefault;
        var onSuccess = options.onSuccess || onSuccessDefault;
        var onError = options.onError || onErrorDefault;
        var onDataError = options.onDataError || onError;
        var onTaskError = options.onTaskError || onError;
        var resultElementId = options.resultElementId || 'celery-result';
        var resultElement = options.resultElement || document.getElementById(resultElementId);
        var onResult = options.onResult || onResultDefault;

        var ProgressSocket = new WebSocket((location.protocol === 'https:' ? 'wss' : 'ws') + '://' +
            window.location.host + progressUrl);

        ProgressSocket.onopen = function (event) {
            ProgressSocket.send(JSON.stringify({'type': 'check_task_completion'}));
        };

        ProgressSocket.onmessage = function (event) {
            var data = JSON.parse(event.data);

            const done = onData(data, onProgress, onSuccess, onTaskError, onDataError, onResult, progressBarElement, progressBarMessageElement, resultElement);

            if (done === true || done === undefined) {
                ProgressSocket.close();
            }
        }
    }
    return {
        onSuccessDefault: onSuccessDefault,
        onResultDefault: onResultDefault,
        onErrorDefault: onErrorDefault,
        onProgressDefault: onProgressDefault,
        initProgressBar: initProgress,
    };
})();
