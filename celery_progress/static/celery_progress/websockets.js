class CeleryWebSocketProgressBar extends CeleryProgressBar {

    constructor(progressUrl, options) {
        super(progressUrl, options);
    }

    async connect() {
        var ProgressSocket = new WebSocket((location.protocol === 'https:' ? 'wss' : 'ws') + '://' +
            window.location.host + this.progressUrl);

        ProgressSocket.onopen = function (event) {
            ProgressSocket.send(JSON.stringify({'type': 'check_task_completion'}));
        };

        const bar = this;
        ProgressSocket.onmessage = function (event) {
            let data;
            try {
                data = JSON.parse(event.data);
            } catch (parsingError) {
                bar.onDataError(bar.progressBarElement, bar.progressBarMessageElement, "Parsing Error")
                throw parsingError;
            }

            const complete = bar.onData(data);

            if (complete === true || complete === undefined) {
                ProgressSocket.close();
            }
        };
    }
}
