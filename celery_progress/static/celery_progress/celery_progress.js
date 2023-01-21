class CeleryProgressBar {

    constructor(progressUrl, options) {
        this.progressUrl = progressUrl;
        options = options || {};
        let progressBarId = options.progressBarId || 'progress-bar';
        let progressBarMessage = options.progressBarMessageId || 'progress-bar-message';
        this.progressBarElement = options.progressBarElement || document.getElementById(progressBarId);
        this.progressBarMessageElement = options.progressBarMessageElement || document.getElementById(progressBarMessage);
        this.onProgress = options.onProgress || this.onProgressDefault;
        this.onSuccess = options.onSuccess || this.onSuccessDefault;
        this.onError = options.onError || this.onErrorDefault;
        this.onTaskError = options.onTaskError || this.onTaskErrorDefault;
        this.onDataError = options.onDataError || this.onError;
        this.onRetry = options.onRetry || this.onRetryDefault;
        this.onIgnored = options.onIgnored || this.onIgnoredDefault;
        let resultElementId = options.resultElementId || 'celery-result';
        this.resultElement = options.resultElement || document.getElementById(resultElementId);
        this.onResult = options.onResult || this.onResultDefault;
        // HTTP options
        this.onNetworkError = options.onNetworkError || this.onError;
        this.onHttpError = options.onHttpError || this.onError;
        this.pollInterval = options.pollInterval || 500;
        // Other options
        this.barColors = Object.assign({}, this.constructor.getBarColorsDefault(), options.barColors);

        let defaultMessages = {
            waiting: 'Waiting for task to start...',
            started: 'Task started...',
        }
        this.messages = Object.assign({}, defaultMessages, options.defaultMessages);
    }

    onSuccessDefault(progressBarElement, progressBarMessageElement, result) {
        result = this.getMessageDetails(result);
        if (progressBarElement) {
            progressBarElement.style.backgroundColor = this.barColors.success;
        }
        if (progressBarMessageElement) {
            progressBarMessageElement.textContent = "Success! " + result;
        }
    }

    onResultDefault(resultElement, result) {
        if (resultElement) {
            resultElement.textContent = result;
        }
    }

    /**
     * Default handler for all errors.
     * @param data - A Response object for HTTP errors, undefined for other errors
     */
    onErrorDefault(progressBarElement, progressBarMessageElement, excMessage, data) {
        progressBarElement.style.backgroundColor = this.barColors.error;
        excMessage = excMessage || '';
        progressBarMessageElement.textContent = "Uh-Oh, something went wrong! " + excMessage;
    }

    onTaskErrorDefault(progressBarElement, progressBarMessageElement, excMessage) {
        let message = this.getMessageDetails(excMessage);
        this.onError(progressBarElement, progressBarMessageElement, message);
    }

    onRetryDefault(progressBarElement, progressBarMessageElement, excMessage, retryWhen) {
        retryWhen = new Date(retryWhen);
        let message = 'Retrying in ' + Math.round((retryWhen.getTime() - Date.now())/1000) + 's: ' + excMessage;
        this.onError(progressBarElement, progressBarMessageElement, message);
    }

    onIgnoredDefault(progressBarElement, progressBarMessageElement, result) {
        progressBarElement.style.backgroundColor = this.barColors.ignored;
        progressBarMessageElement.textContent =  result || 'Task result ignored!'
    }

    onProgressDefault(progressBarElement, progressBarMessageElement, progress) {
        progressBarElement.style.backgroundColor = this.barColors.progress;
        progressBarElement.style.width = progress.percent + "%";
        var description = progress.description || "";
        if (progress.current == 0) {
            if (progress.pending === true) {
                progressBarMessageElement.textContent = this.messages.waiting;
            } else {
                progressBarMessageElement.textContent = this.messages.started;
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
                this.onSuccess(this.progressBarElement, this.progressBarMessageElement, data.result);
            } else if (data.success === false) {
                if (data.state === 'RETRY') {
                    this.onRetry(this.progressBarElement, this.progressBarMessageElement, data.result.message, data.result.when);
                    done = false;
                    delete data.result;
                } else {
                    this.onTaskError(this.progressBarElement, this.progressBarMessageElement, data.result);
                }
            } else {
                if (data.state === 'IGNORED') {
                    this.onIgnored(this.progressBarElement, this.progressBarMessageElement, data.result);
                    delete data.result;
                } else {
                    done = undefined;
                    this.onDataError(this.progressBarElement, this.progressBarMessageElement, "Data Error");
                }
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
    
    static getBarColorsDefault() {
        return {
            success: '#76ce60',
            error: '#dc4f63',
            progress: '#68a9ef',
            ignored: '#7a7a7a'
        };
    }

    static initProgressBar(progressUrl, options) {
        const bar = new this(progressUrl, options);
        bar.connect();
    }
}
