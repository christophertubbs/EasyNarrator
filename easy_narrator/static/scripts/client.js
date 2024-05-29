import {Request} from "./requests.js"
import {closeAllDialogs, generateID, openDialog} from "./utility.js";

function sleep(ms, message) {
    if (ms === null || ms === undefined) {
        ms = 500;
    }
    if (message === null || message === undefined) {
        message = `Waiting ${ms}ms...`;
    }

    console.log(message);
    return new Promise(resolve => setTimeout(resolve, ms));
}

const ReadyState = Object.freeze({
    Connecting: 0,
    Open: 1,
    Closing: 2,
    Closed: 3
})

export class NarratorClient {
    /**
     *
     * @type {WebSocket|null}
     */
    #socket = null;
    #handlers = {};
    #id = null;
    #payloadTypes = {}
    #currentPath = null;
    #onBinary = []

    constructor () {
        this.#id = generateID();
    }

    addHandler = (operation, action) => {
        if (!Object.hasOwn(this.#handlers, operation)) {
            this.#handlers[operation] = [];
        }

        this.#handlers[operation].push(action);
    }

    /**
     *
     * @param {(Blob) => void} action
     */
    addBinaryHandler = (action) => {
        this.#onBinary.push(action);
    }

    clearBinaryHandlers = () => {
        this.#onBinary = [];
    }

    #handleBinary = (data) => {
        this.#onBinary.forEach(action => action(data))
    }

    getID = () => {
        return this.#id;
    }

    #handle = (operation, payload) => {
        if (Object.hasOwn(this.#payloadTypes, operation)) {
            payload = new this.#payloadTypes[operation](payload);
        }

        if (Object.hasOwn(this.#handlers, operation)) {
            this.#handlers[operation].forEach(action => action(payload));
        }
    }

    /**
     *
     * @param payload {Request|object}
     * @param showLoading {Boolean?}
     */
    send = async (payload, showLoading) => {
        if (this.#currentPath === null || this.#currentPath === undefined) {
            throw new Error(`Cannot send message through client '${this.getID()}' - please connect first.`);
        }

        if (typeof showLoading === 'undefined') {
            showLoading = false;
        }

        let rawPayload;
        if (payload instanceof Request) {
            rawPayload = payload.payload;
        }
        else {
            rawPayload = payload;
        }

        if (!Object.hasOwn(rawPayload, "message_id")) {
            rawPayload['message_id'] = generateID()
        }

        const payloadText = JSON.stringify(rawPayload, null, 4)

        if (!this.isConnected()) {
            await this.connect(this.#currentPath)
        }

        console.log(`Sending request: ${payloadText}`);

        while (this.#socket.readyState === ReadyState.Connecting) {
            await sleep(1000);
        }

        this.#socket.send(payloadText);

        if (showLoading) {
            openDialog("#loading-modal")
        }

        if (payload instanceof Request) {
            payload.sent();
        }
    }

    sendRawMessage = (message) => {
        const payload = {
            "message_id": generateID(),
            "message": message
        }
        const requestData = JSON.stringify(payload, null, 4);
        this.#socket.send(requestData);
    }

    #build_websocket_url = (path) => {
        const location = window.location;
        return `ws://${location.host}/${path}`;
    }

    connect = async (path) => {
        this.#socket?.close()

        const url = this.#build_websocket_url(path);
        this.#socket = new WebSocket(url);
        this.#socket.onmessage = this.#handleMessage;
        this.#socket.onopen = this.#handleOpen;
        this.#socket.onclose = this.#handleClose;
        this.#socket.onerror = this.#handleError;

        while (this.#socket.readyState === ReadyState.Connecting) {
            await sleep(1000);
        }

        this.#currentPath = path;
    }

    #handleTextResponse = (text) => {
        console.log(text);
        let deserializedPayload;

        try {
            deserializedPayload = JSON.parse(text);
        } catch (e) {
            debugger;
            console.log("Could not deserialize message from server");
            console.error(e);
            return;
        }

        let operation;
        try {
            operation = deserializedPayload.operation;
        } catch (e) {
            console.error("Could not find the operation on the deserialized payload");
            console.error(e);
            return
        }

        try {
            this.#handle(operation, deserializedPayload);
        } catch (e) {
            console.error("An error occurred while trying to handle an event")
            console.error(e);
        }
    }

    /**
     *
     * @param event {MessageEvent}
     */
    #handleMessage = (event) => {
        const payload = event.data;
        console.log(payload);

        if (payload instanceof Blob) {
            this.#handleBinary(payload);
        }
        else {
            return this.#handleTextResponse(payload);
        }

        closeAllDialogs();
    }

    #handleError = (event) => {
        this.#handle("error", event.data ?? {})
    }

    #handleOpen = (event) => {
        console.log("Connection opened");
        this.#handle("open", event.data ?? {});
    }

    #handleClose = (event) => {
        console.log("Connection closed");
        this.#socket = null;
        this.#handle("closed", event.data ?? {});
    }

    registerPayloadType = (operation, payloadType) => {
        this.#payloadTypes[operation] = payloadType;
    }

    isConnected = () => {
        if (this.#socket === null || this.#socket === undefined) {
            return false;
        }

        return this.#socket.readyState === ReadyState.Open;
    }
}

if (!Object.hasOwn(window, "narrator")) {
    console.log("Creating a new narrator namespace from client.js");
    window.narrator = {};
}

window.narrator.NarratorClient = NarratorClient;