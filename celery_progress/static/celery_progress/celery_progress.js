var CeleryProgressBar = (function () {
    function onSuccessDefault(progressBarElement, progressBarMessageElement, result) {
        progressBarElement.style.backgroundColor = '#76ce60';
        progressBarMessageElement.textContent = "Success!";
    }

    function onResultDefault(resultElement, result) {
        if (resultElement) {
            resultElement.textContent = result;
        }
    }

    /**
     * Default handler for all errors.
     * @param data - A Response object for HTTP errors, undefined for other errors
     */
    function onErrorDefault(progressBarElement, progressBarMessageElement, excMessage, data) {
        progressBarElement.style.backgroundColor = '#dc4f63';
        excMessage = excMessage || '';
        progressBarMessageElement.textContent = "Uh-Oh, something went wrong! " + excMessage;
    }

    function onProgressDefault(progressBarElement, progressBarMessageElement, progress) {
        progressBarElement.style.backgroundColor = '#68a9ef';
        progressBarElement.style.width = progress.percent + "%";
        var description = progress.description || "";
        progressBarMessageElement.textContent = progress.current + ' of ' + progress.total + ' processed. ' + description;
    }

    async function updateProgress (progressUrl, options) {
        options = options || {};
        var progressBarId = options.progressBarId || 'progress-bar';
        var progressBarMessage = options.progressBarMessageId || 'progress-bar-message';
        var progressBarElement = options.progressBarElement || document.getElementById(progressBarId);
        var progressBarMessageElement = options.progressBarMessageElement || document.getElementById(progressBarMessage);
        var onProgress = options.onProgress || onProgressDefault;
        var onSuccess = options.onSuccess || onSuccessDefault;
        var onError = options.onError || onErrorDefault;
        var onTaskError = options.onTaskError || onError;
        var onNetworkError = options.onNetworkError || onError;
        var onHttpError = options.onHttpError || onError;
        var onDataError = options.onDataError || onError;
        var pollInterval = options.pollInterval || 500;
        var resultElementId = options.resultElementId || 'celery-result';
        var resultElement = options.resultElement || document.getElementById(resultElementId);
        var onResult = options.onResult || onResultDefault;


        const getMessageDetails = function (result) {
            if (resultElement) {
                return ''
            } else {
                return result || '';
            }
        };
        let response;
        try {
            response = await fetch(progressUrl);
        } catch (networkError) {
            onNetworkError(progressBarElement, progressBarMessageElement, "Network Error");
            throw networkError;
        }

        if (response.status === 200) {
            let data;
            try {
                data = await response.json();
            } catch (parsingError) {
                onDataError(progressBarElement, progressBarMessageElement, "Parsing Error")
                throw parsingError;
            }

            if (data.progress) {
                onProgress(progressBarElement, progressBarMessageElement, data.progress);
            }
            if (data.complete === false) {
                setTimeout(updateProgress, pollInterval, progressUrl, options);
            } else {
                if (data.success === true) {
                    onSuccess(progressBarElement, progressBarMessageElement, getMessageDetails(data.result));
                } else if (data.success === false) {
                    onTaskError(progressBarElement, progressBarMessageElement, getMessageDetails(data.result));
                } else {
                    onDataError(progressBarElement, progressBarMessageElement, "Data Error");
                }
                if (data.hasOwnProperty('result')) {
                    onResult(resultElement, data.result);
                }
            }
        } else {
            onHttpError(progressBarElement, progressBarMessageElement, "HTTP Code " + response.status, response);
        }
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
