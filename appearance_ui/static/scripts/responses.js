/**
 * Base class for responses that'll come from the server via REST or a websocket
 */
export class Response {}

export class OpenResponse extends Response{
    constructor (payload) {
        super();
        console.log("Connected")
        console.log(payload)
    }
}

export class AcknowledgementResponse extends Response {
    messageID;
    message;

    constructor ({messageID, message}) {
        super();
        this.messageID = messageID;
        this.message = message;
    }
}

export class KillResponse extends Response {
    messageID;
    message;
    constructor ({messageID, message}) {
        super();
        this.message = message;
        this.messageID = messageID
    }
}

window.appearance.AcknowledgementResponse = AcknowledgementResponse;
window.appearance.OpenResponse = OpenResponse;
window.appearance.KillResponse = KillResponse;