var CeleryProgressBar = (function () {
    function onSuccessDefault(progressBarElement, progressBarMessageElement, result) {
        progressBarElement.style.backgroundColor = '#76ce60';
        progressBarMessageElement.innerHTML = "Success!";
    }

    function onResultDefault(resultElement, result) {
        if (resultElement) {
            resultElement.innerHTML = result;
        }
    }

    function onErrorDefault(progressBarElement, progressBarMessageElement, excMessage) {
        progressBarElement.style.backgroundColor = '#dc4f63';
        progressBarMessageElement.innerHTML = "Uh-Oh, something went wrong! " + excMessage;
    }

    function onProgressDefault(progressBarElement, progressBarMessageElement, progress) {
        progressBarElement.style.backgroundColor = '#68a9ef';
        progressBarElement.style.width = progress.percent + "%";
        var description = progress.description || "";
        progressBarMessageElement.innerHTML = progress.current + ' of ' + progress.total + ' processed. ' + description;
    }

    function updateProgress (progressUrl, options) {
        options = options || {};
        var progressBarId = options.progressBarId || 'progress-bar';
        var progressBarMessage = options.progressBarMessageId || 'progress-bar-message';
        var progressBarElement = options.progressBarElement || document.getElementById(progressBarId);
        var progressBarMessageElement = options.progressBarMessageElement || document.getElementById(progressBarMessage);
        var onProgress = options.onProgress || onProgressDefault;
        var onSuccess = options.onSuccess || onSuccessDefault;
        var onError = options.onError || onErrorDefault;
        var pollInterval = options.pollInterval || 500;
        var resultElementId = options.resultElementId || 'celery-result';
        var resultElement = options.resultElement || document.getElementById(resultElementId);
        var onResult = options.onResult || onResultDefault;


        fetch(progressUrl).then(function(response) {
            response.json().then(function(data) {
                if (data.progress) {
                    onProgress(progressBarElement, progressBarMessageElement, data.progress);
                }
                if (!data.complete) {
                    setTimeout(updateProgress, pollInterval, progressUrl, options);
                } else {
                    if (data.success) {
                        onSuccess(progressBarElement, progressBarMessageElement, data.result);
                    } else {
                        onError(progressBarElement, progressBarMessageElement, data.result);
                    }
                    if (data.result) {
                        onResult(resultElement, data.result);
                    }
                }
            });
        });
    }
    return {
        onSuccessDefault: onSuccessDefault,
        onResultDefault: onResultDefault,
        onErrorDefault: onErrorDefault,
        onProgressDefault: onProgressDefault,
        updateProgress: updateProgress,
        initProgressBar: updateProgress,  // just for api cleanliness
    };
})();
