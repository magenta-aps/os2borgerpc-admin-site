class PolicyList {
    editModal = bootstrap.Modal.getOrCreateInstance(document.getElementById("editpolicyscriptdialog"))
    amountOfNewScripts = 0;
    tableBody = document.getElementById("policy-table-body")

    constructor() {
        BibOS.addTemplate("policylist-item", "#policy-item-template")
        document.querySelectorAll("#policy-item-template input").forEach(input => input.disabled = true)
        document.querySelectorAll("#editpolicyscriptdialog input").forEach(input => input.disabled = true)
        document.querySelector("#editpolicyscriptdialog")?.addEventListener("shown.bs.modal", (e) => {
            e.target.querySelector(".modal-body>input")?.focus()
        })
        document.querySelector("#updategroupform").addEventListener("submit", this.verifyPolicies.bind(this))
    }

    /**
     * The final handling of whether a policy is valid before it's submitted to the server, triggered when saving group settings
     */
    verifyPolicies(event) {
        const hiddenFields = Array.from(this.tableBody.querySelectorAll(".policy-script-param"))
        for (const hiddenField of hiddenFields) {
            // Before the submit event is sent to the server, we can make a simple check to see if all required values are filled
            // This preserves the users input in case they forget to fill out an input field
            if (hiddenField.dataset.isrequired){
                const row = hiddenField.closest("tr")
                if (hiddenField.type !== "file" && !hiddenField.value.trim()) {
                    displayError(hiddenField, row)
                    event.preventDefault()
                    break;
                } else if (hiddenField.type === "file") {
                    // We can't check on the value of the <input type="file"> element itself
                    // Since those input fields never store their data in the value attribute
                    // Instead we can check if the print field has any contents, either text or child nodes
                    const printElement = hiddenField.nextElementSibling.querySelector(".policy-script-print-value")
                    const hasContent = printElement.textContent.trim() !== "" || printElement.children.length > 0;
                    if (!hasContent) {
                        displayError(hiddenField, row)
                        event.preventDefault()
                        break;
                    }
                }
                else if (row) {
                    row.classList.remove("table-danger")
                }
            }
        }

        /**
         * If an error in the policy is discovered when attempting to save it, this will display that error to the user
         */
        function displayError(hiddenField, row) {
            const message = `Script:\n
                    ${hiddenField.parentElement.getAttribute("data-name") || gettext("Unknown script")}
                    \n${gettext("has empty required input fields")}`
            displayToast(message, "error")
            if (row) {
                row.classList.add("table-danger")
                row.scrollIntoView({"behavior": "smooth"})
            }
        }
    }

    /**
     * This HTML snippet should match what's inside item.html
     * Used by renderScriptFields which is run by addToPolicy
     */
    hiddenParamField(name, type, required, default_value) {
        return `
            <input class="policy-script-param ${type === "FILE" ? "d-none" : ""}"
                type="${type === "FILE" ? "file" : "hidden"}"
                name="${name}"
                value="${type === "BOOLEAN" ? 'True" checked' : type === "TEXT_FIELD" ? default_value.split(",")[0] : default_value}"
                ${type === "TEXT_FIELD" ? `default_value="${default_value}"` : ""}
                data-inputtype="${type}"
                ${required == "True" ? "data-isrequired='true'" : ""}
            />
        `
    }

    /**
     * This HTML snippet should match what's inside item.html
     * Used by renderScriptFields which is run by addToPolicy
     */
    visibleParamField(input) {
        if (input.type === "TEXT_FIELD") {
            input.default_value = input.default_value.split(",")[0]
        }
        return `
            <div class="policy-script-print">
                <span class="policy-script-print-name pe-1">${input.name}${input.required == "True" ? '*' : ''}:</span>
                <span class="policy-script-print-value">
                    ${input.type === "BOOLEAN"
                        ? '<input type="checkbox" class="form-check-input" checked disabled>'
                        : input.default_value} 
                </span>
            </div>`
    }

    /**
     * Called by list.html when you click a script from the search results to add it to the policy
     */
    addToPolicy(scriptId, scriptName, scriptPk, scriptInputs) {
        const itemHtml = BibOS.expandTemplate("policylist-item", {
            ps_pk: "new_" + this.amountOfNewScripts,
            script_pk: scriptPk,
            name: scriptName,
            position: "new_" + this.amountOfNewScripts,
            submit_name: "group_policies",
        })

        this.tableBody.insertAdjacentHTML("beforeend", itemHtml)
        document.getElementById("filtersearch-group_policies").scrollIntoView()

        const rowNode = this.tableBody.querySelector("tr:last-of-type") // Give renderScriptFields access to the relevant <tr>
        this.renderScriptFields(scriptId, "new_" + this.amountOfNewScripts, scriptInputs, rowNode)
        this.updateNew("group_policies")
    }

    /**
    * Called at the end when you add or remove a script from a policy
    */
    updateNew(id = "group_policies") {
        let num = 0
        document.querySelectorAll(`#${id} input.policy-script-pos`).forEach((element) => {
            if (element.value.startsWith("new_")) {
                element.parentElement.querySelector("input.policy-script-name").name = id + "_new_" + num
                element.parentElement.querySelectorAll("input.policy-script-param").forEach((param, index) => param.name = `${id}_new_${num}_param_${index}`)
                element.value = "new_" + num
                num++
            }
        })
        this.amountOfNewScripts = num;
    }

    /**
     * Renders the non-editable list of parameters and their values for a newly added associated script that hasn't yet been saved
     */
    renderScriptFields(pk, scriptPk, scriptInputs, rowNode) {
        if (!scriptInputs || scriptInputs.length === 0) {
            rowNode.querySelector(".edit-policy-btn")?.classList.add("invisible")
            return; // Save some processing since the rest of the function will do nothing
        }
        // If we come directly from adding a new script, django template variable "params" will only be #PARAMS#, so we need to render the fields dynamically
        let param_fields = ""
        // generate the hidden input fields and divs to render the parameters for the selected script
        for (let i = 0; i < scriptInputs.length; i++) {
            const paramName = `group_policies_${scriptPk}_param_${i}`
            param_fields += this.hiddenParamField(
                paramName,
                scriptInputs[i].type,
                scriptInputs[i].required,
                scriptInputs[i].default_value,
            )
            param_fields += this.visibleParamField(scriptInputs[i])
        }

        rowNode.querySelector(`[data-pk="policy-script-${pk}"]`)?.insertAdjacentHTML("beforeend", param_fields)
    }
    /**
     * Triggered when clicking the submit button while editing the parameters for a specific policy script
     * Fetches data from the visible parameters and updates the hidden parameters based on the changes.
     * Additionally it updates the values displayed next to each script?
     */
    submitEditDialog(policy_id) {
        const wrapper = document.getElementById(policy_id)
        // Note: This loop omits select/options which don't have .form-control but instead .form-select
        const modalInputs = document.querySelectorAll(
            "#editpolicyscriptdialog .modal-body .form-control",
        )
        /* Check that each of our mandatory inputs has a value (or that its
           corresponding hidden input field already has a value) */
        let count = 0
        modalInputs.forEach((inputElement) => {
            let hiddenFieldName = inputElement.getAttribute("name").substring(5)
            let hiddenField = wrapper.querySelector(`input[name="${hiddenFieldName}"]`)
            if (hiddenField.getAttribute("data-isrequired")) {
                if (
                    inputElement.type === "file" &&
                    inputElement.files.length === 0 &&
                    hiddenField.files.length === 0
                ) {
                    /* If the hidden input field has a value, then it's fine if
                       this one doesn't -- we won't overwrite it */
                    inputElement.classList.add("is-invalid")
                    inputElement.focus()
                    return false;
                } else if (inputElement.type !== "checkbox" && inputElement.value.trim().length === 0) {
                    inputElement.classList.add("is-invalid")
                    inputElement.focus()
                    return false
                }
            }

            inputElement.classList.remove("is-invalid")
            count += 1
        })

        if (count !== modalInputs.length) {
            return false
        }

        // loop over inputs inside the modal, and set their corresponding hidden input fields in the group form
        //
        modalInputs.forEach((inputElement) => {
            let hiddenFieldName = inputElement.getAttribute("name").substring(5)
            let hiddenField = wrapper.querySelector(`input[name="${hiddenFieldName}"]`)

            let visibleValueField = null
            let hiddenFieldNextSibling = hiddenField.nextElementSibling

            while (hiddenFieldNextSibling) {
                if (hiddenFieldNextSibling.matches(".policy-script-print")) {
                    visibleValueField = hiddenFieldNextSibling.querySelector(
                        ".policy-script-print-value",
                    )
                    break
                }
                hiddenFieldNextSibling = hiddenFieldNextSibling.nextElementSibling
            }
            if (!visibleValueField) return;

            if (inputElement.type === "file") {
                // If a new file was selected set that in hiddenparams, otherwise set the selected file
                if (inputElement.files.length !== 0) {
                    hiddenField.files = inputElement.files
                    visibleValueField.textContent = inputElement.files[0].name
                }
            } else if (inputElement.type === "checkbox") {
                hiddenField.value = inputElement.checked ? "True" : "False"
                visibleValueField.innerHTML = `<input type="checkbox" class="form-check-input" disabled ${inputElement.checked ? "checked" : ""}>`
            } else if (inputElement.type === "password") {
                hiddenField.value = inputElement.value
                visibleValueField.textContent = "•••••"

                // This workaround prevents the browser from prompting to save a password
                inputElement.type = "text"
                inputElement.classList.add("d-none")
                inputElement.parentElement.appendChild(inputElement.cloneNode())
                inputElement.remove()
            } else {
                hiddenField.value = inputElement.value
                visibleValueField.textContent = inputElement.value
            }
        })
        this.editModal.hide()
        return false
    }

    /**
     * Renders the form in the modal, created when clicking to edit the values for the input parameters of an associated script,
     * based on data in the hidden params (policy-script-param)
     */
    editScriptInputParams(clickedElement, defaultValues) {
        // the modal body that contains the input fields
        const modalbody = document.querySelector("#editpolicyscriptdialog .modal-body")
        modalbody.innerHTML = ""

        // loop over all input fields, and render them in the modal
        clickedElement.closest("tr").querySelectorAll(".policy-script-param").forEach((inputparam, index) => {
            const paramType = this.getFieldType(inputparam.getAttribute("data-inputtype"))
            const wrapperDiv = document.createElement("div")
            wrapperDiv.classList.add("mb-3")
            let newElement

            if (paramType === "textfield") {
                newElement = document.createElement("select")

                /* defaultValues will be 'None' if we come directly from adding a new script.
                 This is because the values are taken from django template variable "params",
                 which will only be #PARAMS# when we come directly from adding a new script */
                let options
                if (defaultValues !== "None") {
                    options = defaultValues[index].split(",")
                } else {
                    options = inputparam.getAttribute("default_value").split(",")
                }
                for (let option of options) {
                    option = option.trim()
                    newElement.insertAdjacentHTML("beforeend", `<option value="${option}">${option}</option>`)
                }
            } else {
                newElement = document.createElement("input")
                // Only change type on inputs
                newElement.type = paramType
            }

            if (paramType === "file") {
                /* In principle, it'd be nice (for display purposes) to copy the
                 FileList from the hidden input into the modal dialog -- but
                 this confuses Firefox 65 enormously, and when we try to copy
                 the FileList back again, it gets cleared! */
                newElement.files = inputparam.files
            } else {
                if (paramType === "checkbox") {
                    newElement.checked = inputparam.value === "True"
                }
                newElement.value = inputparam.value
            }

            // set the common attributes name, id, class
            newElement.name = "edit_" + inputparam.name
            newElement.id = "edit_" + inputparam.name
            newElement.className =
                paramType !== "checkbox"
                    ? "form-control"
                    : "form-control form-check-input"
            newElement.setAttribute("aria-describedby", `invalidFeedback${index}`)

            // Create a label element
            let label = inputparam.nextElementSibling.querySelector(
                ".policy-script-print-name",
            )
            wrapperDiv.insertAdjacentHTML("beforeend", `
                <label htmlFor="${newElement.id}">${label.textContent}</label>
            `)
            wrapperDiv.appendChild(newElement)

            wrapperDiv.insertAdjacentHTML("beforeend", `
                <div id="invalidFeedback${index}" class="invalid-feedback">
                    ${gettext("Please fill out this field")}
                </div>
            `)
            modalbody.appendChild(wrapperDiv)
            new bootstrap.Tooltip(newElement)
        })

        this.editModal.show()
    }

    getFieldType(type) {
        const typeMapping = {
            INT: "number",
            STRING: "text",
            FILE: "file",
            DATE: "date",
            BOOLEAN: "checkbox",
            TIME: "time",
            PASSWORD: "password",
            TEXT_FIELD: "textfield",
        }

        return typeMapping[type] || "text"
    }

    /**
     * Called when you click to remove an associated script from the policy
     */
    removeItem(clickedElem, id) {
        // Find the closest parent <tr> element
        const rowElement = clickedElem.closest("tr")

        if (rowElement) {
            rowElement.remove()
        }

        this.updateNew(id)
    }

    /**
     * When you click to save group settings this is called to redo the counts for script positions
     */
    updateScriptPositions() {
        let fields = document.getElementsByClassName("position-field")

        let i = 0
        for (let item of fields) {
            item.value = i
            i++
        }
    }
}


const policyListHandler = new PolicyList()
