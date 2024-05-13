export class Request {
    send_handlers;

    constructor () {
        this.send_handlers = [];
    }

    getRawPayload = () => {
        throw new Error("getRawPayload was not implemented for this request");
    }

    getOperation = () => {
        throw new Error("getOperation was not implemented for this request");
    }

    sent = () => {
        for (let handler of this.send_handlers) {
            handler();
        }
    }

    onSend = (handler) => {
        this.send_handlers.push(handler);
    };
}

export class FileSelectionRequest extends Request {
    operation = "load"
    path
    row_count
    constructor ({path, row_count}) {
        super();

        this.path = path
        if (row_count !== null && row_count !== undefined) {
            this.row_count = row_count
        }
        else {
            this.row_count = 20;
        }
    }

    getRawPayload = () => {
        return {
            "operation": this.operation,
            "path": this.path,
            "row_count": this.row_count
        };
    }

    getOperation = () => {
        return "load"
    }
}

export class KillRequest extends Request {
    operation = "kill"

    getRawPayload = () => {
        return {
            "operation": this.operation
        }
    }

    getOperation = () => {
        return "kill";
    }
}

window.appearance.FileSelectionRequest = FileSelectionRequest;
window.appearance.KillRequest = KillRequest;