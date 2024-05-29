import {closeAllDialogs, openDialog} from "./utility.js";
import {
    AcknowledgementResponse,
    AudioResponse,
    DataTransferCompleteResponse,
    KillResponse, LoadResponse,
    OpenResponse
} from "./responses.js";
import {ListValue, ListValueAction, ListValueEvent} from "./value.js";
import {Application} from "./application.js";

const PREVIOUS_PATH_KEY = "previousPath";

function initializeApplication() {
    Object.defineProperty(
        narrator,
        "app",
        {
            value: new Application({
                audioElement: $("audio")[0],
                speakerInput: document.getElementById("speaker-selection"),
                modelInput: document.getElementById("model-selection"),
                languageInput: document.getElementById("language-input")
            })
        }
    );

    Object.defineProperty(
        narrator,
        "currentlyLoading",
        {
            value: new ListValue(
                [],
                function (event) {
                    if (event.action === ListValueAction.ADD) {
                        openLoadModal({});
                    } else if (event.action === ListValueAction.DELETE) {
                        if (Object.keys(narrator.onLoadComplete).includes(event.modifiedValue)) {
                            narrator.onLoadComplete[event.modifiedValue](event);
                        }
                    }

                    if (event.data.length === 0) {
                        closeAllDialogs();
                    }
                }
            ),
            enumerable: true,
            writable: false
        }
    );

    Object.defineProperty(
        narrator,
        "onLoadComplete",
        {
            /** @type {{string: (ListValueEvent) => null}} **/
            value: {},
            writable: false,
            enumerable: true
        }
    )
}

function initializeEditor() {
    const textAreaSelection = $("#text-field");
    textAreaSelection.val(narrator.app.text);
    const textArea = textAreaSelection[0];
    narrator.editor = CodeMirror.fromTextArea(
        textArea,
        {
            lineWrapping: true,
            viewportMargin: Infinity
        }
    );
    narrator.editor.on("change", function(){
        narrator.app.text = narrator.editor.getValue();
    })
}

/**
 *
 * @param {Event} event
 */
function setSpeed(event) {
    narrator.app.audio.playbackRate = Number(event.target.value);
}

async function initializeClient() {

    const client = new narrator.NarratorClient();

    client.addHandler(
        "connection_opened",
        () => {
            narrator.app.connected = true;
            console.log("The connection has been opened");
            toggleContentLoadStatus();
        }
    );
    client.addHandler(
        "closed",
        () => {
            narrator.app.connected = false;
            toggleContentLoadStatus();
        }
    );
    client.addHandler("error", handleError);
    client.addHandler("kill", closeApplication);
    client.addHandler("transfer_complete", completeLoading);
    client.addHandler(
        "load",
        openLoadModal
    )
    client.addHandler(
        "read",
        textRead
    )
    
    client.addBinaryHandler((data) => {
        narrator.app.addTrack(data);
    })

    client.registerPayloadType("connection_opened", OpenResponse);
    client.registerPayloadType("acknowledgement", AcknowledgementResponse);
    client.registerPayloadType("kill", KillResponse)
    client.registerPayloadType("read", AudioResponse)
    client.registerPayloadType("transfer_complete", DataTransferCompleteResponse);
    client.registerPayloadType("load", LoadResponse);

    Object.defineProperty(
        narrator,
        "client",
        {
            value: client,
            enumerable: true
        }
    )

    narrator.app.connected = false;
    await narrator.client.connect("ws");
}

function toggleContentLoadStatus() {
    const contentToShow = $(narrator.app.connected ? ".narrator-when-connected" : ".narrator-when-disconnected");
    const contentToHide = $(!narrator.app.connected ? ".narrator-when-disconnected" : ".narrator-when-connected");

    contentToShow.show();
    contentToHide.hide();
}

async function handleError(payload) {
    $("#failed_message_type").text(Boolean(payload['message_type']) ? payload["message_type"] : "Unknown")
    $("#failed-message-id").text(payload['message_id']);
    $("#error-message").text(payload['error_message']);
    openDialog("#error-dialog");
}

async function closeApplication() {
    window.close();
}

async function getData(path) {
    const request = new narrator.FileSelectionRequest({path: path})

    /**
     * @type {HTMLSpanElement}
     */
    const filenameSpan = document.getElementById("currently-loading");
    filenameSpan.innerText = path;
    request.onSend(openLoadModal);

    await narrator.client.send(request);
}

async function startClosingApplication() {
    const request = new narrator.KillRequest();
    await narrator.client.send(request);
}

function initializeOpenPath() {
    $("#load-dialog").dialog({
        modal: true,
        autoOpen: false,
        width: "60%",
        height: 150
    })

    const openPathInput = $("input#open-path");

    openPathInput.autocomplete({
        source: "navigate"
    });

    $("#open-dataset-button").on("click", loadDataClicked);
}

function initializeModals() {
    $(".narrator-modal:not(#load-dialog):not(#loading-modal)").dialog({
        modal: true,
        autoOpen: false
    });

    $("#error-dialog").dialog({
        modal: true,
        autoOpen: false,
        width: "20%"
    });

    $("#loading-modal").dialog({
        modal: true,
        autoOpen: false,
        width: "50%",
        height: 200
    })
}

async function initialize() {
    initializeApplication();
    initializeModals();
    initializeEditor();
    $("#loading-progress-bar").progressbar({value: false});
    $("button").button();
    $("#content").tabs();
    toggleContentLoadStatus();

    Object.defineProperty(
        narrator,
        "refreshTabs",
        {
            value: () => {
                const tabsView = $("#content").tabs();
                tabsView.tabs("refresh");
                tabsView.off("click");
                tabsView.on("click", "span.ui-icon-close", function() {
                    narrator.removeData(this.dataset.data_id);
                });
            },
            enumerable: true
        }
    );

    initializeOpenPath()

    $("#close-loading-modal-button").on("click", closeLoadingModal);
    $("#load-button").on("click", launchLoadDialog);
    $("#kill-button").on("click", startClosingApplication);
    $("#narrate-button").on("click", readTextClicked);
    $("#audio-box select").on("change", setSpeed);

    await initializeClient();
}

async function loadDataClicked() {
    const url = $("input#open-path").val();
    await getData(url);
    localStorage.setItem(PREVIOUS_PATH_KEY, url);
}

function textRead() {
    closeAllDialogs();
    console.log("Text read, now loading audio...");
    narrator.app.trackIndex = 0;
    /** @type {HTMLAudioElement} **/
    const audio = narrator.app.audio;
    audio.play().then();
}

async function readTextClicked() {
    let configuration = {
        name: narrator.app.selectedModel,
        speed: narrator.app.audio.playbackRate
    }

    if (narrator.app.currentModel.is_multi_lingual) {
        configuration['language'] = narrator.app.selectedLanguage;
    }

    if (narrator.app.currentModel.is_multi_speaker) {
        configuration['speaker'] = narrator.app.selectedSpeaker;
    }

    const request = new narrator.ReadRequest({
        text: narrator.app.text,
        configuration: configuration
    });

    narrator.currentlyLoading.push(request.message_id);
    narrator.onLoadComplete[request.message_id] = textRead;
    narrator.app.clearTracks();
    await narrator.client.send(request, true);
}
/**
 *
 * @param {DataTransferCompleteResponse} response
 * @returns {Promise<void>}
 */
async function completeLoading(response) {
    narrator.currentlyLoading.remove(response.messageID);
}

document.addEventListener("DOMContentLoaded", async function() {
    await initialize();
});

function closeLoadingModal() {
    closeAllDialogs();
}

function launchLoadDialog() {
    const previousPath = localStorage[PREVIOUS_PATH_KEY];

    if (previousPath) {
        $("input#open-path").val(previousPath);
    }

    openDialog("#load-dialog")
}

/**
 *
 * @param {LoadResponse|undefined} response
 */
function openLoadModal(response) {
    if (!response) {
        response = new LoadResponse({});
    }

    if (typeof response.percentComplete === 'undefined' || response.percentComplete === null) {
        $("#loading-progress-bar").progressbar({value: false});
    } else {
        $("#loading-progress-bar").progressbar({value: response.percentComplete});
    }

    if (response.message) {
        $("#loading-message").text(response.message);
    }

    if (response.itemCount) {
        $("#loading-total-count").text(response.itemCount);
        $("#loading-completion-count").text(response.countComplete);
    }

    openDialog("#loading-modal");
}