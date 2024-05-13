import {closeAllDialogs, openDialog} from "./utility.js";
import {AcknowledgementResponse, KillResponse, OpenResponse} from "./responses.js";
import {BooleanValue, ListValue, ListValueAction} from "./value.js";

const PREVIOUS_PATH_KEY = "previousPath";

function initializeBackingVariables() {
    const connected = BooleanValue.True;
    connected.onUpdate(socketIsConnected);

    Object.defineProperty(
        appearance,
        "connected",
        {
            get() {
                return connected.isTrue;
            },
            set(newValue) {
                if (newValue) {
                    return connected.toTrue
                }
                return connected.toFalse
            },
            enumerable: true
        }
    )

    Object.defineProperty(
        appearance,
        "datasets",
        {
            value: new ListValue(
                [],
                toggleContentLoadStatus
            ),
            enumerable: true
        }
    )
}

async function initializeClient() {

    const client = new appearance.AppearanceClient();

    client.addHandler("open", () => appearance.connected = true);
    client.addHandler("closed", () => appearance.connected = false);
    client.addHandler("error", handleError);
    client.addHandler("kill", closeApplication);

    client.registerPayloadType("connection_opened", OpenResponse);
    client.registerPayloadType("acknowledgement", AcknowledgementResponse);
    client.registerPayloadType("kill", KillResponse)

    Object.defineProperty(
        appearance,
        "client",
        {
            value: client,
            enumerable: true
        }
    )

    appearance.connected = false;
    await appearance.client.connect("ws");
}

/**
 * @member {boolean}
 */
function hasContent() {
    return false
}

function toggleContentLoadStatus() {
    const contentToShow = $(hasContent() ? "#no-content-block" : "#content");
    const contentToHide = $(!hasContent() ? "#content" : "#no-content-block");

    contentToShow.show();
    contentToHide.hide();
}

function contentHasBeenLoaded(wasLoaded, isNowLoaded) {
    if (wasLoaded === isNowLoaded) {
        return;
    }

    const contentToHide = $(isNowLoaded ? "#no-content-block" : "#content");
    const contentToShow = $(isNowLoaded ? "#content" : "#no-content-block");

    contentToHide.hide();
    contentToShow.show();

    console.log("The content loaded state should now be reflected");
}

function socketIsConnected(wasConnected, isNowConnected) {
    if (wasConnected === isNowConnected) {
        return;
    }

    const contentToHide = $(isNowConnected ? ".appearance-when-disconnected" : ".appearance-when-connected");
    const contentToShow = $(isNowConnected ? ".appearance-when-connected" : ".appearance-when-disconnected");

    contentToHide.hide();
    contentToShow.show();
}

async function handleError(payload) {
    $("#failed_message_type").text(Boolean(payload['message_type']) ? payload["message_type"] : "Unknown")
    $("#failed-message-id").text(payload['message_id']);
    $("#error-message").text(payload['error_message']);
    openDialog("#error-dialog");
}

async function closeApplication(payload) {
    window.close();
}

async function getData(path) {
    const request = new appearance.FileSelectionRequest({path: path})

    /**
     * @type {HTMLSpanElement}
     */
    const filenameSpan = document.getElementById("currently-loading");
    filenameSpan.innerText = path;
    request.onSend(function() {
        openDialog("#loading-modal");
    });

    await appearance.client.send(request);
}

async function startClosingApplication() {
    const request = new appearance.KillRequest();
    await appearance.client.send(request);
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

/**
 *
 * @param view {View}
 */
function addView(view) {
    try {
        view.render("#content", "#content-tabs")
    } catch (e) {
        console.error(e);
    }
    closeAllDialogs();
}

function initializeModals() {
    $(".appearance-modal:not(#load-dialog):not(#loading-modal)").dialog({
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
    initializeBackingVariables();
    initializeModals();
    $("#loading-progress-bar").progressbar({value: false});
    $("button").button();
    $("#content").tabs();
    toggleContentLoadStatus();

    Object.defineProperty(
        appearance,
        "refreshTabs",
        {
            value: () => {
                const tabsView = $("#content").tabs();
                tabsView.tabs("refresh");
                tabsView.off("click");
                tabsView.on("click", "span.ui-icon-close", function() {
                    appearance.removeData(this.dataset.data_id);
                });
            },
            enumerable: true
        }
    );

    Object.defineProperty(
        appearance,
        "removeData",
        {
            value: (data_id) => {
                const responseIndex = appearance.datasets.findIndex((response) => response.data_id === data_id);

                if (responseIndex >= 0) {
                    appearance.datasets.removeAt(responseIndex);
                }
            }
        }
    )

    initializeOpenPath()

    $("#close-loading-modal-button").on("click", closeLoadingModal);
    $("#load-button").on("click", launchLoadDialog);
    $("#kill-button").on("click", startClosingApplication);

    await initializeClient();
}

function removeTab(removalEvent) {

}

async function loadDataClicked(event) {
    const url = $("input#open-path").val();
    await getData(url);
    localStorage.setItem(PREVIOUS_PATH_KEY, url);
}

document.addEventListener("DOMContentLoaded", async function(event) {
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