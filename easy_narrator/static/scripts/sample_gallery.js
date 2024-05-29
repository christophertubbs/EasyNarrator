/**
 * @typedef ModelOption
 * @property {string} text
 * @property {string} value
 * @property {string[]|null|undefined} speakers
 * @property {string[]|null|undefined} languages
 */

/**
 * @typedef DatasetOption
 * @property {string} text
 * @property {string} value
 * @property {ModelOption[]} models
 */

import {closeAllDialogs, openDialog} from "./utility.js";

/** @type {DatasetOption[]} **/
let SAMPLE_OPTIONS;

function applyEventHandlers() {
    $("#dataset-selector").on("change", datasetChanged);
    $("#model-selector").on("change", modelChanged);
    $("#load-sample-button").on("click", getSample);
}

function datasetChanged(event) {
    const datasetValue = $("#dataset-selector").val();
    const selectedDataset = SAMPLE_OPTIONS.find(
        (value, index, options) => {
            return value.value === datasetValue;
        }
    )
    setModelOptions(selectedDataset.models);
}

/**
 *
 * @param {Event} event
 */
function modelChanged(event) {
    const datasetValue = $("#dataset-selector").val();
    const selectedDataset = SAMPLE_OPTIONS.find(
        (value, index, options) => {
            return value.value === datasetValue;
        }
    )
    const modelValue = event.currentTarget.value;
    const selectedModel = selectedDataset.models.find(value => value.value === modelValue)
    setLanguageOptions(selectedModel.languages)
    setSpeakerOptions(selectedModel.speakers);
}

async function getSample() {
    const url = "/sample";
    const data = {
        model: $("#model-selector").val(),
        language: $("#language-selector").val(),
        speaker: $("#speaker-selector").val()
    }

    fetch(
        url,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data)
        }
    ).then(
        response => {
            if (response.status >= 400) {
                return Promise.reject(response)
            } else {
                return response.blob()
            }
        }
    ).then(
        loadAudio,
        showResponseError
    );
}

function loadAudio(audioResponse) {
    let audio = URL.createObjectURL(audioResponse);

    /** @type {HTMLAudioElement} **/
    let audioElement = document.getElementById("narration")
    audioElement.src = audio;
    audioElement.play().then();
}

async function getSampleOptions() {
    const url = "/sample/list";
    fetch(
        url
    ).then(
        response => {
            if (response.status >= 400) {
                reject(response);
            } else {
                return response.json()
            }
        }
    ).then(
        setDatasetOptions,
        showResponseError
    )
}

/**
 *
 * @param {Error} error
 */
function showResponseError(error) {
    if (error instanceof Response) {
        error.text().then(
            message => {
                try {
                    const errorResponse = JSON.parse(message);
                    reportError(errorResponse.error_message, errorResponse.message_type)
                } catch (e) {
                    reportError(message)
                }
            }
        )
    } else if (error instanceof Error) {
        reportError(`${error.name}: ${error.message}`);
    }
}

function reportError(message, messageType) {
    if (messageType) {
        $("#failed_message_type").text(messageType);
    } else {
        $("#failed_message_type").text("");
    }
    $("#error-message").text(message);
    openDialog("#error-dialog")
}

/**
 *
 * @param {{"samples": DatasetOption[]}} options
 */
function setDatasetOptions(options) {
    SAMPLE_OPTIONS = options.samples;

    const datasetSelector = $("#dataset-selector")
    datasetSelector.empty()

    for (let datasetIndex = 0; datasetIndex < SAMPLE_OPTIONS.length; datasetIndex++) {
        let markup;
        let selectedDataset = SAMPLE_OPTIONS[datasetIndex];

        if (datasetIndex === 0) {
            setModelOptions(selectedDataset.models);
            markup = $(`<option value="${selectedDataset.value}" selected>${selectedDataset.value}</option>`);
        } else {
            markup = $(`<option value="${selectedDataset.value}">${selectedDataset.value}</option>`);
        }

        datasetSelector.append(markup)
    }
}

/**
 *
 * @param {ModelOption[]} options
 */
function setModelOptions(options) {
    const modelSelector = $("#model-selector");
    modelSelector.empty();

    for (let modelIndex = 0; modelIndex < options.length; modelIndex++) {
        let model = options[modelIndex]
        let markup;

        if (modelIndex === 0) {
            setLanguageOptions(model.languages);
            setSpeakerOptions(model.speakers);

            markup = $(`<option value="${model.value}" selected>${model.text}</option>`);
        } else {
            markup = $(`<option value="${model.value}">${model.text}</option>`);
        }

        modelSelector.append(markup);
    }
}

/**
 *
 * @param {string[]} options
 */
function setLanguageOptions(options) {
    const languageSelector = $("#language-selector");
    languageSelector.empty();

    if (options && options.length > 0) {
        $("#language-box").show();

        for (let languageIndex = 0; languageIndex < options.length; languageIndex++) {
            let markup;
            let value = options[languageIndex];

            if (languageIndex === 0) {
                markup = $(`<option value="${value}" selected>${value}</option>`)
            } else {
                markup = $(`<option value="${value}">${value}</option>`)
            }

            languageSelector.append(markup);
        }
    } else {
        $("#language-box").hide();
    }
}

function setSpeakerOptions(options) {
    const speakerSelector = $("#speaker-selector");
    speakerSelector.empty();

    if (options && options.length > 0) {
        $("#speaker-box").show();

        for (let speakerIndex = 0; speakerIndex < options.length; speakerIndex++) {
            let markup;
            let value = options[speakerIndex];

            if (speakerIndex === 0) {
                markup = $(`<option value="${value}" selected>${value}</option>`)
            } else {
                markup = $(`<option value="${value}">${value}</option>`)
            }

            speakerSelector.append(markup);
        }
    } else {
        $("#speaker-box").hide();
    }
}

function applyUI() {
    $("button").button();
    $("#loading-progress-bar").progressbar({value: false});

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
    });
}

document.addEventListener("DOMContentLoaded", async function() {
    applyUI();
    openDialog("#loading-modal");
    applyEventHandlers();
    await getSampleOptions();
    closeAllDialogs();
});