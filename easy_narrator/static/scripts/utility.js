export function closeAllDialogs() {
    $(".narrator-dialog").dialog("close");
}

export function openDialog(selector) {
    closeAllDialogs();
    $(selector).dialog("open");
}

export function generateID(length) {
    if (length === null || length === undefined) {
        length = 8;
    }

    const characterSet = "0123456789ABCDEF";
    function getRandomCharacter() {
        const characterIndex = Math.floor(Math.random() * characterSet.length);
        return characterSet[characterIndex];
    }

    let generatedID = "";

    for (let counter = 0; counter < length; counter++) {
        generatedID += getRandomCharacter();
    }

    return generatedID;
}

/**
 * Get the names of all member fields in a list of objects
 *
 * @param objects {({}|Object)[]|{}|Object} A list of objects that have common fields
 * @param all {boolean?} Retrieve every field name, even if they aren't shared by all members
 * @returns {string[]}
 */
export function getColumnNames(objects, all) {
    if (!Array.isArray(objects)) {
        return Object.entries(objects)
            .filter(
                ([key, value]) => typeof value !== 'function'
            )
            .map(
                ([key, value]) => key
            )
    }

    if (all === null || all === undefined) {
        all = false;
    }

    let commonFields = [];

    for (let objectIndex = 0; objectIndex < objects.length; objectIndex++) {
        let obj = objects[objectIndex];

        if (objectIndex === 0 || all) {
            for (let [key, value] of Object.entries(obj)) {
                if (!['function', 'object'].includes(typeof value)) {
                    commonFields.push(key);
                }
            }
        }
        else if (!all) {
            let keysToRemove = [];
            let thisObjectsKeys = Object.keys(obj);

            for (let key of commonFields) {
                if (!thisObjectsKeys.includes(key)) {
                    keysToRemove.push(key);
                }
            }

            commonFields = commonFields.filter(
                (value) => !keysToRemove.includes(value)
            )
        }
    }

    return commonFields;
}