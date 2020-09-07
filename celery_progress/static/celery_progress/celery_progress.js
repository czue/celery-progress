class CeleryProgressBar {

    constructor(progressUrl, options) {
        this.progressUrl = progressUrl;
        options = options || {};
        let progressBarId = options.progressBarId || 'progress-bar';
        let progressBarMessage = options.progressBarMessageId || 'progress-bar-message';
        this.progressBarElement = options.progressBarElement || document.getElementById(progressBarId);
        this.progressBarMessageElement = options.progressBarMessageElement || document.getElementById(progressBarMessage);
        this.onProgress = options.onProgress || CeleryProgressBar.onProgressDefault;
        this.onSuccess = options.onSuccess || CeleryProgressBar.onSuccessDefault;
        this.onError = options.onError || CeleryProgressBar.onErrorDefault;
        this.onTaskError = options.onTaskError || this.onError;
        this.onDataError = options.onDataError || this.onError;
        let resultElementId = options.resultElementId || 'celery-result';
        this.resultElement = options.resultElement || document.getElementById(resultElementId);
        this.onResult = options.onResult || CeleryProgressBar.onResultDefault;
        // HTTP options
        this.onNetworkError = options.onNetworkError || this.onError;
        this.onHttpError = options.onHttpError || this.onError;
        this.pollInterval = options.pollInterval || 500;
    }

    static onSuccessDefault(progressBarElement, progressBarMessageElement, result) {
        progressBarElement.style.backgroundColor = '#76ce60';
        progressBarMessageElement.textContent = "Success! " + result;
    }

    static onResultDefault(resultElement, result) {
        if (resultElement) {
            resultElement.textContent = result;
        }
    }

    /**
     * Default handler for all errors.
     * @param data - A Response object for HTTP errors, undefined for other errors
     */
    static onErrorDefault(progressBarElement, progressBarMessageElement, excMessage, data) {
        progressBarElement.style.backgroundColor = '#dc4f63';
        excMessage = excMessage || '';
        progressBarMessageElement.textContent = "Uh-Oh, something went wrong! " + excMessage;
    }

    static onProgressDefault(progressBarElement, progressBarMessageElement, progress) {
        progressBarElement.style.backgroundColor = '#68a9ef';
        progressBarElement.style.width = progress.percent + "%";
        var description = progress.description || "";
        if (progress.current == 0) {
            if (progress.pending === true) {
                progressBarMessageElement.textContent = 'Waiting for task to start...';
            } else {
                progressBarMessageElement.textContent = 'Task started...';
            }
        } else {
            progressBarMessageElement.textContent = progress.current + ' of ' + progress.total + ' processed. ' + description;
        }
    }

    getMessageDetails(result) {
        if (this.resultElement) {
            return ''
        } else {
            return result || '';
        }
    }

    /**
     * Process update message data.
     * @return true if the task is complete, false if it's not, undefined if `data` is invalid
     */
    onData(data) {
        let done = false;
        if (data.progress) {
            this.onProgress(this.progressBarElement, this.progressBarMessageElement, data.progress);
        }
        if (data.complete === true) {
            done = true;
            if (data.success === true) {
                this.onSuccess(this.progressBarElement, this.progressBarMessageElement, this.getMessageDetails(data.result));
            } else if (data.success === false) {
                this.onTaskError(this.progressBarElement, this.progressBarMessageElement, this.getMessageDetails(data.result));
            } else {
                done = undefined;
                this.onDataError(this.progressBarElement, this.progressBarMessageElement, "Data Error");
            }
            if (data.hasOwnProperty('result')) {
                this.onResult(this.resultElement, data.result);
            }
        } else if (data.complete === undefined) {
            done = undefined;
            this.onDataError(this.progressBarElement, this.progressBarMessageElement, "Data Error");
        }
        return done;
    }

    async connect() {
        let response;
        try {
            response = await fetch(this.progressUrl);
        } catch (networkError) {
            this.onNetworkError(this.progressBarElement, this.progressBarMessageElement, "Network Error");
            throw networkError;
        }

        if (response.status === 200) {
            let data;
            try {
                data = await response.json();
            } catch (parsingError) {
                this.onDataError(this.progressBarElement, this.progressBarMessageElement, "Parsing Error")
                throw parsingError;
            }

            const complete = this.onData(data);

            if (complete === false) {
                setTimeout(this.connect.bind(this), this.pollInterval);
            }
        } else {
            this.onHttpError(this.progressBarElement, this.progressBarMessageElement, "HTTP Code " + response.status, response);
        }
    }

    static initProgressBar(progressUrl, options) {
        const bar = new this(progressUrl, options);
        bar.connect();
    }
}
