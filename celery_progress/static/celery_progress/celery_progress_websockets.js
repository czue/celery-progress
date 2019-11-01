var CeleryWebSocketProgressBar = (function () {
    function onSuccessDefault(progressBarElement, progressBarMessageElement) {
        CeleryProgressBar.onSuccessDefault(progressBarElement, progressBarMessageElement);
    }

    function onResultDefault(resultElement, result) {
        CeleryProgressBar.onResultDefault(resultElement, result);
    }

    function onErrorDefault(progressBarElement, progressBarMessageElement) {
        CeleryProgressBar.onErrorDefault(progressBarElement, progressBarMessageElement);
    }

    function onProgressDefault(progressBarElement, progressBarMessageElement, progress) {
        CeleryProgressBar.onProgressDefault(progressBarElement, progressBarMessageElement, progress);
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

            if (data.progress) {
                onProgress(progressBarElement, progressBarMessageElement, data.progress);
            }
            if (data.complete) {
                if (data.success) {
                    onSuccess(progressBarElement, progressBarMessageElement);
                } else {
                    onError(progressBarElement, progressBarMessageElement);
                }
                if (data.result) {
                    onResult(resultElement, data.result);
                }
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
