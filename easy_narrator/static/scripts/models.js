export class NarratorConfig {
    #model_name
    #speed

    constructor({model_name, speed}) {
        this.#model_name = typeof model_name !== 'undefined' ? model_name : "tts_models/en/ljspeech/tacotron2-DDC_ph"
        this.#speed = typeof speed === 'number' ? speed : 1.0
    }

    get model_name() {
        return this.#model_name
    }

    get speed() {
        return this.#speed;
    }

    get raw_configuration() {
        return {
            model_name: this.model_name,
            speed: this.speed
        }
    }
}

export class VCTKVITSConfig extends NarratorConfig {
    #speaker
    constructor({speaker, speed}) {
        super({model_name: "tts_models/en/vctk/vits", speed: speed})
        this.#speaker = speaker;
    }

    get speaker() {
        return this.#speaker;
    }

    get raw_configuration() {
        let configuration = super.raw_configuration;
        configuration.speaker = this.speaker;
        return configuration;
    }
}

export class XTTSV2Config extends NarratorConfig {
    #speaker
    #language;

    constructor({speaker, language, speed}) {
        super({model_name: "tts_models/multilingual/multi-dataset/xtts_v2" , speed: speed})
        this.#speaker = speaker;
        this.#language = language || "en";
    }

    get speaker() {
        return this.#speaker;
    }

    get raw_configuration() {
        let configuration = super.raw_configuration;
        configuration.speaker = this.speaker;
        configuration.language = this.#language;
        return configuration;
    }
}


export function getConfigClassForModel(modelName) {
    let configClass = NarratorConfig;

    switch (modelName) {
        case "tts_models/en/vctk/vits":
            configClass = VCTKVITSConfig
            break;
        case "tts_models/multilingual/multi-dataset/xtts_v2":
            configClass = XTTSV2Config
            break;
    }

    return configClass
}