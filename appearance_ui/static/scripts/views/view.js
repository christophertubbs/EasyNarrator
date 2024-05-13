import {createFieldSet} from "../elements.js";
import {Response} from "../responses.js";

/**
 * Builds a view on the page that allows a user to inspect loaded netcdf data
 */
export class View {
    /**
     * The data that helped spawn this view
     *
     * @member {Response}
     */
    data


    /**
     * An identifier for the overall data held within this view
     *
     * @member {string}
     */
    data_id


    /**
     * The anchor that activates the tab for this when clicked
     *
     * @member {HTMLAnchorElement|undefined}
     */
    tabLink;

    /**
     * Constructor
     *
     * @param data The response from the server that provided this data
     */
    constructor (data) {
        this.data = data;
        this.data_id = data.data_id
    }

    getName() {
        return this.data_id;
    }

    open = () => {
        this.tabLink.click();
    }

    get #tabID() {
        return `${this.data_id}-tab`
    }

    /**
     * Add a tab for this dataset in the set of tabs
     *
     * @param tabSelector {string}
     */
    #addTab = (tabSelector) => {
        const tabs = $(tabSelector);

        // Only add this tab if there isn't already one like it
        if ($(`${tabSelector} li#${this.#tabID}`).length === 0) {
            /**
             * @type {HTMLLIElement}
             */
            const tab = document.createElement("li")
            tab.id = this.#tabID

            /**
             *
             * @type {HTMLAnchorElement}
             */
            const tabLink = document.createElement("a")
            tabLink.href = `#${this.data_id}`;
            tabLink.innerText = this.getName();

            const tabCloseButton = document.createElement("span");
            tabCloseButton.className = "ui-icon ui-icon-close";
            tabCloseButton.dataset['data_id'] = this.data_id
            tabCloseButton.dataset['container_selector'] = `#${this.data_id}`
            tabCloseButton.dataset['tab_selector'] = `#${this.#tabID}`

            this.tabLink = tabLink;

            tab.appendChild(tabLink);
            tab.appendChild(tabCloseButton);
            tabs.append(tab);
        }
    }

    /**
     * Generate content specific to this view to put on the page
     *
     * @returns {HTMLElement}
     */
    renderContent = () => {
        const metadataFieldset = createFieldSet(
            `${this.data_id}-metadata`,
            `${this.data_id}-metadata`,
            "Metadata"
        );

        const idLabel = document.createElement("b");
        idLabel.innerText = "Generated ID: ";
        idLabel.className = "appearance-detail-label";

        const idTag = document.createElement("span");
        idTag.innerText = this.data_id;
        idTag.className = 'appearance-detail';

        metadataFieldset.appendChild(idLabel);
        metadataFieldset.appendChild(idTag);
        metadataFieldset.appendChild(document.createElement("br"))

        return metadataFieldset
    }

    /**
     * Render this view at the given tab container
     *
     * @param tabContainerSelector {string} The selector for the containers where tab data is added
     * @param tabListSelector {string} The selector for the list of tabs where the handle will be placed
     */
    render = (tabContainerSelector, tabListSelector) => {
        /**
         * The container that holds all tab content
         *
         * @type {jQuery}
         */
        const tabContainer = $(tabContainerSelector);

        if (!tabContainer) {
            throw new Error(`No elements could be found at '${tabContainerSelector}' - a new view cannot be rendered`)
        }

        if ($(tabListSelector).length === 0) {
            throw new Error(`No tab list could be found at '${tabListSelector}' - a new view cannot be rendered`)
        }

        if ($(`#${this.data_id}`).length > 0) {
            console.warn(`There is already a view for dataset ${this.data_id}`)
        }

        /**
         *
         * @type {HTMLDivElement}
         */
        const newTab = document.createElement("div");
        newTab.id = this.data_id;

        const containerCSSClasses = [
            `appearance-container`,
            'appearance-tab',
            `appearance-dataset`
        ]

        newTab.className = containerCSSClasses.join(" ");
        newTab.dataset['dataset'] = this.data_id;
        newTab.dataset['tab'] = this.#tabID;

        /**
         *
         * @type {HTMLDivElement}
         */
        const innerContainer = document.createElement("div");
        innerContainer.id = `${this.data_id}-field-wrapper`;

        const innerContainerCSSClasses = [
            "appearance-field-wrapper"
        ]

        innerContainer.className = innerContainerCSSClasses.join(" ");

        const innerContent = this.renderContent();

        if (innerContent !== null && typeof innerContent !== 'undefined') {
            innerContainer.appendChild(innerContent);
        }
        else {
            console.error("Content could not be generated to place within a view")
        }

        newTab.appendChild(innerContainer);

        tabContainer.append(newTab)

        $(".appearance-accordion").accordion({
            heightStyle: "content"
        });

        this.#addTab(tabListSelector);
        //tabContainer.tabs("refresh");
        appearance.refreshTabs()

        this.open();
    }
}

