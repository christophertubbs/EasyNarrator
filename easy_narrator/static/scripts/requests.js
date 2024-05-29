import {NarratorConfig} from "./models.js";
import {generateID, openDialog} from "./utility.js";

export class Request {
    send_handlers;
    message_id;

    constructor () {
        this.send_handlers = [];
        this.message_id = generateID()
    }

    get payload() {
        throw new Error("getRawPayload was not implemented for this request");
    }

    get operation() {
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

    constructor ({path}) {
        super();
        this.path = path
        this.onSend(function() {
            openDialog("#loading-modal");
        })
    }

    get payload() {
        return {
            "message_id": this.message_id,
            "operation": this.operation,
            "path": this.path
        };
    }

    get operation() {
        return "load"
    }
}

export class KillRequest extends Request {
    operation = "kill"

    get payload() {
        return {
            "message_id": this.message_id,
            "operation": this.operation
        }
    }

    get operation() {
        return "kill";
    }
}

export class ReadRequest extends Request {
    operation = "read"
    text
    /** @type {object} **/
    configuration

    constructor({text, configuration}) {
        super();
        this.text = text;
        this.configuration = typeof configuration !== 'undefined' ? configuration : {};
        this.onSend(function() {
            openDialog("#loading-modal");
        })
    }

    get payload() {
        return {
            "message_id": this.message_id,
            "operation": this.operation,
            "text": this.text,
            configuration: this.configuration
        }
    }

    get operation() {
        return "read"
    }
}

window.narrator.FileSelectionRequest = FileSelectionRequest;
window.narrator.KillRequest = KillRequest;
window.narrator.ReadRequest = ReadRequest;