import {BooleanValue, NumericValue, ListValue} from "./value.js";

/**
 * @typedef Model
 * @property {boolean} is_multi_lingual
 * @property {boolean} is_multi_speaker
 * @property {string[]|null|undefined} languages
 * @property {string[]|null|undefined} speakers
 */

export class Application {
    /** @type {BooleanValue} **/
    #connected= BooleanValue.True;

    /** @type {ListValue<string>} **/
    #tracks = new ListValue(
        [],
        (event) => {
            if (event.data.length === 0) {
                $(this.audioBox).hide();
            } else {
                $(this.audioBox).show();
            }
        }
    );

    #trackIndex = new NumericValue(
        0,
        (oldValue, newValue) => {
            this.audio = newValue
        }
    );

    /** @type {HTMLAudioElement} **/
    #audioElement;

    /** @type {HTMLSelectElement} **/
    #speakerInput;

    /** @type {HTMLSelectElement} **/
    #modelInput;

    /** @type {HTMLSelectElement} **/
    #languageInput;

    /** @type {{string: Model}} **/
    #models;

    constructor({audioElement, speakerInput, modelInput, languageInput}) {
        if (!speakerInput) {
            throw new Error("Cannot create Application - not element for the speaker input was passed");
        } else {
            this.#speakerInput = speakerInput;
            this.#speakerInput.onchange = (event) => {
                this.selectedSpeaker = event.currentTarget.value;
            }
        }

        if (modelInput) {
            this.#modelInput = modelInput;
            this.#modelInput.onchange = (event) => {
                this.selectedModel = event.currentTarget.value;
                this.setSpeakers();
                this.setLanguages();
            }
        }
        if (!modelInput) {
            throw new Error("Cannot create Application - no element for the model input was passed");
        }

        if (languageInput) {
            this.#languageInput = languageInput;
            this.#languageInput.onchange = (event) => {
                this.selectedLanguage = event.currentTarget.value;
            }
        } else {
            throw new Error("Cannot create Application - no element for the language input was passed");
        }

        if (!audioElement) {
            audioElement = $("audio")[0];
        }

        this.#audioElement = audioElement;
        this.#audioElement.onended = () => {
            setTimeout(
                this.#trackIndex.increment,
                this.trackDelay
            );
        }

        this.fetchModels();
    }

    fetchModels = () => {
        fetch("/models/parameters").then(
            response => response.json()
        ).then(models => {
            this.#models = models;
            const selectedModel = this.selectedModel || this.defaultModel;

            $(this.#modelInput).empty()

            for (let modelName of Object.keys(models)){
                let optionAttributes = {
                    value: modelName
                }

                if (modelName === selectedModel) {
                    optionAttributes['selected'] = true;
                }

                let modelEntry = $(document.createElement("option")).attr(optionAttributes).text(modelName)[0];
                $(this.#modelInput).append(modelEntry);
            }

            this.setLanguages(selectedModel);
            this.setSpeakers(selectedModel);
        });
    }

    setLanguages = (modelName) => {
        /** @type {Model|undefined} **/
        const modelData = modelName ? this.#models[modelName] : this.#models[this.selectedModel];

        const languageInput = $(this.#languageInput);
        languageInput.empty();

        if (!modelData || !modelData.is_multi_lingual || modelData.languages.length <= 1) {
            languageInput.val(undefined);
            languageInput.hide();
            return;
        }

        if (!modelData.languages.includes(this.selectedLanguage)) {
            this.selectedLanguage = modelData.languages.includes("en") ? "en" : modelData.languages[0];
        }

        for (let language of modelData['languages']) {
            if (language === this.selectedLanguage) {
                languageInput.append(`<option value="${language}" selected>${language}</option>`);
            } else {
                languageInput.append(`<option value="${language}">${language}</option>`);
            }
        }

        languageInput.show();
    }

    setSpeakers = (modelName) => {
        /** @type {Model|undefined} **/
        const modelData = modelName ? this.#models[modelName] : this.#models[this.selectedModel];

        const speakerInput = $(this.#speakerInput);
        speakerInput.empty();

        if (!modelData || !modelData.is_multi_speaker || modelData.speakers.length <= 1) {
            speakerInput.val(undefined);
            speakerInput.hide();
            return;
        }

        if (!modelData.speakers.includes(this.selectedSpeaker)) {
            this.selectedSpeaker = modelData.speakers[0];
        }

        for (let speaker of modelData['speakers']) {
            if (speaker === this.selectedSpeaker) {
                speakerInput.append(`<option value="${speaker}" selected>${speaker}</option>`);
            } else {
                speakerInput.append(`<option value="${speaker}">${speaker}</option>`);
            }
        }

        speakerInput.show();
    }

    get selectedModelKey() {
        return "selected-model";
    }

    get connected() {
        return this.#connected.isTrue;
    }

    set connected(newValue) {
        if (newValue) {
            return this.#connected.toTrue;
        }
        return this.#connected.toFalse;
    }

    get storage() {
        return localStorage;
    }

    get selectedModel() {
        if (this.selectedModelKey in this.storage) {
            return this.storage[this.selectedModelKey];
        }
        return undefined;
    }

    set selectedModel(modelName) {
        if (modelName !== '' && modelName !== null && typeof modelName !== 'undefined') {
            this.storage[this.selectedModelKey] = modelName;
        }
    }

    get selectedSpeakerKey() {
        return "selected-speaker";
    }

    get selectedSpeaker() {
        return this.storage[this.selectedSpeakerKey];
    }

    set selectedSpeaker(speakerName) {
        if (speakerName !== '' && speakerName !== null && typeof speakerName !== 'undefined') {
            this.storage[this.selectedSpeakerKey] = speakerName;
        }
    }

    get selectedLanguageKey() {
        return 'seleted-language';
    }

    get selectedLanguage() {
        return this.storage[this.selectedLanguageKey];
    }

    set selectedLanguage(language) {
        this.storage[this.selectedLanguageKey] = language;
    }

    get textKey() {
        return "narrator-text"
    }

    get text() {
        return this.storage[this.textKey] || '';
    }

    set text(newText) {
        if (typeof newText !== 'undefined') {
            this.storage[this.textKey] = newText;
        }
    }

    get defaultModel() {
        return "tts_models/en/vctk/vits";
    }

    get trackCount() {
        return Object.keys(this.#tracks).length;
    }

    get audio() {
        return this.#audioElement;
    }

    set audio(index) {
        if (this.trackCount === 0) {
            console.log("Cannot change audio track - no audio tracks have been loaded");
            return;
        } else if (index >= this.#tracks.length) {
            index = 0;
        } else if (index < 0) {
            index = this.#tracks.length - 1;
        }

        this.#audioElement.src = this.#tracks.at(index);
    }

    /**
     * @type {HTMLElement}
     */
    get audioBox() {
        return this.audio.parentElement;
    }

    get trackDelay() {
        return 1;
    }

    get trackIndex() {
        return this.#trackIndex.get();
    }

    set trackIndex(newValue) {
        this.#trackIndex.set(newValue);
    }

    clearTracks = () => {
        while (this.#tracks.length) {
            let sound = this.#tracks.pop()
            URL.revokeObjectURL(sound);
        }
    }

    /**
     *
     * @param {Blob|string} audioTrack
     */
    addTrack = (audioTrack) => {
        if (audioTrack instanceof Blob) {
            audioTrack = URL.createObjectURL(audioTrack);
        }
        console.log(`Adding a new track to the narration at index ${this.trackCount}`);
        this.#tracks.push(audioTrack);
    }

    nextSound = () => {
        this.trackIndex = this.trackIndex + 1;
    }

    previousSound = () => {
        this.trackIndex = this.trackIndex - 1;
    }

    /** @type {Model} **/
    get currentModel() {
        return this.#models[this.selectedModel || this.defaultModel];
    }
}