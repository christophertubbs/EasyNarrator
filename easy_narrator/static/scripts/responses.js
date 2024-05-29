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

    constructor ({message_id, message}) {
        super();
        this.messageID = message_id;
        this.message = message;
    }
}

export class KillResponse extends Response {
    messageID;
    message;
    constructor ({message_id, message}) {
        super();
        this.message = message;
        this.messageID = message_id
    }
}

export class AudioResponse extends Response {
    messageID;
    audio;
    audioIndex;
    audioCount;

    constructor({message_id, audio, audio_index, audio_count}) {
        super();
        if (typeof audio === 'string') {
            // Convert the byte string to an ArrayBuffer
            let arrayBuffer = new ArrayBuffer(audio.length);
            let uint8Array = new Uint8Array(arrayBuffer);
            for (let i = 0; i < audio.length; i++) {
              uint8Array[i] = audio.charCodeAt(i);
            }

            // Create a Blob from the ArrayBuffer
            audio = new Blob([arrayBuffer], { type: 'application/octet-stream' });
        }
        this.messageID = message_id;
        this.audio = audio;
        this.audioIndex = audio_index;
        this.audioCount = audio_count;
    }
}

export class DataTransferCompleteResponse extends Response {
    messageID;

    constructor({message_id}) {
        super()
        this.messageID = message_id;
    }
}

export class LoadResponse extends Response {
    #percentComplete;
    #messageID;
    #message;
    #itemCount;
    #countComplete;
    #operation;

    constructor({message_id, message, percent_complete, item_count, count_complete, operation}) {
        super();
        this.#messageID = message_id;
        this.#message = message || "Loading Data...";
        this.#percentComplete = percent_complete || false;
        this.#itemCount = item_count;
        this.#countComplete = count_complete || 0;
        this.#operation = operation || "load";
    }

    get percentComplete() {
        return this.#percentComplete;
    }

    get messageID() {
        return this.#messageID;
    }

    get message() {
        return this.#message;
    }

    get itemCount() {
        return this.#itemCount;
    }

    get countComplete() {
        return this.#countComplete || 0;
    }

    get operation() {
        return this.#operation;
    }
}

window.narrator.AcknowledgementResponse = AcknowledgementResponse;
window.narrator.OpenResponse = OpenResponse;
window.narrator.KillResponse = KillResponse;
window.narrator.AudioResponse = AudioResponse;
window.narrator.DataTransferCompleteResponse = DataTransferCompleteResponse;
window.narrator.LoadResponse = LoadResponse;