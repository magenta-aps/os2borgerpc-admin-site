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

    verifyPolicies(event) {
        const inputFields = Array.from(this.tableBody.querySelectorAll(".policy-script-param"))
        for (const inputField of inputFields) {
            // Before the submit event is sent to the server, we can make a simple check to see if all required values are filled
            // This preserves the users input in case they forget to fill out an input field
            if (inputField.dataset.isrequired){
                const row = inputField.closest("tr")
                if (inputField.type !== "file" && !inputField.value.trim()) {
                    displayError(inputField, row)
                    event.preventDefault()
                    break;
                } else if (inputField.type === "file") {
                    // We can't check on the value of the <input type="file"> element itself
                    // Since those input fields never store their data in the value attribute
                    // Instead we can check if the print field has any contents, either text or child nodes
                    const printElement = inputField.nextElementSibling.querySelector(".policy-script-print-value")
                    const hasContent = printElement.textContent.trim() !== "" || printElement.children.length > 0;
                    if (!hasContent) {
                        displayError(inputField, row)
                        event.preventDefault()
                        break;
                    }
                }
                else if (row) {
                    row.classList.remove("table-danger")
                }
            }
        }

        function displayError(inputField, row) {
            const message = `Script:\n
                    ${inputField.parentElement.getAttribute("data-name") || gettext("Unknown script")}
                    \n${gettext("Has required input fields")}`
            console.log("message:", message)
            displayToast(message, "error")
            if (row) {
                row.classList.add("table-danger")
                row.scrollIntoView({"behavior": "smooth"})
            }
        }
    }

    // These two snippets of HTML should match what's inside item.html
    hiddenParamField(name, type, required, default_value) {
        return `
            <input class="policy-script-param ${type === "FILE" ? "d-none" : ""}"
                type="${type === "FILE" ? "file" : "hidden"}"
                name="${name}"
                value="${type === "BOOLEAN" ? 'True" checked' : type === "TEXT_FIELD" ? default_value.split(",")[0] : default_value}"
                ${type === "TEXT_FIELD" ? `default_value="${default_value}"` : ""}
                data-inputtype="${type}"
                ${required ? "data-isrequired='true'" : ""}                
            />
        `;

    }

    visibleParamField(input) {
        if (input.type === "TEXT_FIELD") {
            input.default_value = input.default_value.split(",")[0]
        }
        return `
            <div class="policy-script-print">
                <strong class="policy-script-print-name"> ${input.name}:</strong>
                <span class="policy-script-print-value">
                    ${input.type === "BOOLEAN"
            ? '<input type="checkbox" class="form-check-input" checked disabled>'
            : input.default_value} 
                </span>
            </div>`

    }

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
            console.log("Script input", i, scriptInputs[i])
            param_fields += this.hiddenParamField(
                paramName,
                scriptInputs[i].type,
                scriptInputs[i].required,
                scriptInputs[i].default_value,
            )
            param_fields += this.visibleParamField(scriptInputs[i])
        }
        console.log("param fields:",param_fields)

        rowNode.querySelector(`[data-pk="policy-script-${pk}"]`)?.insertAdjacentHTML("beforeend", param_fields)
    }

    submitEditDialog(policy_id) {
        const wrapper = document.getElementById(policy_id)
        const modalInputs = document.querySelectorAll(
            "#editpolicyscriptdialog .modal-body .form-control",
        )
        /* Check that each of our mandatory inputs has a value (or that its
           corresponding hidden input field already has a value) */
        let count = 0
        modalInputs.forEach((inputElement) => {
            let inputName = inputElement.getAttribute("name").substring(5)
            let inputField = wrapper.querySelector('input[name="' + inputName + '"]')
            if (inputField.getAttribute("data-isrequired")) {
                console.log("input field:",inputField)
                console.log("input element:",inputElement)
                console.log("input element type:",inputElement.type)
                if (
                    inputElement.type === "file" &&
                    inputElement.files.length === 0 &&
                    inputField.files.length === 0
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
        modalInputs.forEach((inputElement) => {
            let inputName = inputElement.getAttribute("name").substring(5)
            let inputField = wrapper.querySelector(`input[name="${inputName}"]`)

            let visibleValueField = null
            let nextSibling = inputField.nextElementSibling

            while (nextSibling) {
                if (nextSibling.matches(".policy-script-print")) {
                    visibleValueField = nextSibling.querySelector(
                        ".policy-script-print-value",
                    )
                    break
                }
                nextSibling = nextSibling.nextElementSibling
            }
            if (!visibleValueField) return;

            if (inputElement.type === "file") {
                if (inputElement.files.length !== 0) {
                    inputField.files = inputElement.files
                    visibleValueField.textContent = inputElement.files[0].name
                }
            } else if (inputElement.type === "checkbox") {
                inputField.value = inputElement.checked ? "True" : "False"
                visibleValueField.innerHTML = `<input type="checkbox" class="form-check-input" disabled ${inputElement.checked ? "checked" : ""}>`
            } else if (inputElement.type === "password") {
                inputField.value = inputElement.value
                visibleValueField.textContent = "•••••"

                // This workaround prevents the browser from prompting to save a password
                inputElement.type = "text"
                inputElement.classList.add("d-none")
                const clonedElement = inputElement.cloneNode()
                inputElement.parentElement.appendChild(clonedElement)
                inputElement.remove()
            } else {
                inputField.value = inputElement.value
                visibleValueField.textContent = inputElement.value
            }
        })
        this.editModal.hide()
        return false
    }

    scriptEdit(clickedElement, defaultValues) {
        // the modal body that contains the input fields
        const modalbody = document.querySelector("#editpolicyscriptdialog .modal-body")
        modalbody.innerHTML = ""

        // loop over all input fields, and render them in the modal
        clickedElement.closest("tr").querySelectorAll(".policy-script-param").forEach((inputparam, index) => {
            const paramType = this.getFieldType(inputparam.getAttribute("data-inputtype"))
            const wrapperDiv = document.createElement("div")
            let newElement;

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


    removeItem(clickedElem, id) {
        // Find the closest parent <tr> element
        const rowElement = clickedElem.closest("tr")

        if (rowElement) {
            rowElement.remove()
        }

        this.updateNew(id)
    }

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
