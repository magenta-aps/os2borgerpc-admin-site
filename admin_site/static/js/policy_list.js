;(function (BibOS, $) {
  if (!document.getElementById("policylist-templates")) {
    alert(
      "policy_list.js loaded without templates present" +
        "\n" +
        "Did you forget to include system/policy_list/templates.html?",
    )
    return
  }

  var PolicyList = function () {
    this.scriptInputs = []
    // These two snippets of HTML should match what's inside item.html
    this.hiddenParamField = function (name, type, required, default_value) {
      return (
        '<input class="policy-script-param' +
        (type == "FILE" ? " phantom" : "") +
        '" type="' +
        (type == "FILE" ? "file" : "hidden") +
        '" name="' +
        name +
        '" value="' +
        (type == "BOOLEAN"
          ? 'True" checked="true"'
          : type == "TEXT_FIELD"
            ? default_value.split(",")[0]
            : default_value) +
        (type == "TEXT_FIELD" ? '" default_value="' + default_value : "") +
        '" data-inputtype="' +
        type +
        '"' +
        (required == "True" ? ' required="required"' : "") +
        "/>"
      )
    }
    this.visibleParamField = function (input) {
      if (input.type == "TEXT_FIELD") {
        input.default_value = input.default_value.split(",")[0]
      }
      return (
        '<div class="policy-script-print"><strong class="policy-script-print-name">' +
        input.name +
        ': </strong><span class="policy-script-print-value">' +
        (input.type == "BOOLEAN"
          ? '<input type="checkbox" class="form-check-input" checked disabled>'
          : input.default_value) +
        "</span></div>"
      )
    }
  }

  $.extend(PolicyList.prototype, {
    init: function () {
      BibOS.addTemplate("policylist-item", "#policy-item-template")
      $("#policy-item-template input").attr("disabled", "disabled")
      $("#editpolicyscriptdialog input").attr("disabled", "disabled")
      $("#editpolicyscriptdialog").on("shown", function () {
        $(".editpolicyscript-field").first().trigger("focus")
      })
    },
    addToPolicy: function (id, scriptId, scriptName, scriptPk, scriptInputs) {
      var num_new = $("#" + id + "_new_entries").val()
      var item = $(
        BibOS.expandTemplate("policylist-item", {
          ps_pk: "new_" + num_new,
          script_pk: scriptPk,
          name: scriptName,
          position: "new_" + num_new,
          submit_name: id,
        }),
      )
      this.scriptInputs = scriptInputs
      item.insertBefore($("#" + id + "_new_entries"))
      this.updateNew(id)
    },
    updateNew: function (id) {
      var num = 0
      $("#" + id + " input.policy-script-pos").each(function () {
        var t = $(this),
          p = t.parent()

        if (t.val().match(/^new_/)) {
          p.find("input.policy-script-name").attr("name", id + "_new_" + num)
          p.find("input.policy-script-param").each(function (i) {
            $(this).attr("name", id + "_new_" + num + "_param_" + i)
          })
          t.val("new_" + num)
          num++
        }

        $("#" + id + "_new_entries").val(num)
      })
    },
    renderScriptFields: function (pk, scriptPk, submitName) {
      // If we come directly from adding a new script, django template variable "params" will only be #PARAMS#, so we need to render the fields dynamically
      var param_fields = ""

      // generate the hidden input fields and divs to render the parameters for the selected script
      for (var i = 0; i < BibOS.PolicyList.scriptInputs.length; i++) {
        paramName = submitName + "_" + scriptPk + "_param_" + i
        param_fields += this.hiddenParamField(
          paramName,
          BibOS.PolicyList.scriptInputs[i].type,
          BibOS.PolicyList.scriptInputs[i].required,
          BibOS.PolicyList.scriptInputs[i].default_value,
        )
        param_fields += this.visibleParamField(BibOS.PolicyList.scriptInputs[i])
      }

      // output the fields
      $('[data-pk="policy-script-' + pk + '"]')
        .last()
        .append(param_fields)
    },
  })

  BibOS.PolicyList = new PolicyList()
  $(function () {
    BibOS.PolicyList.init()
  })
})(BibOS, $)

function scriptEdit(clickedElement, defaultValues) {
  const editModal = $("#editpolicyscriptdialog")

  // the modal body that contains the input fields
  const modalbody = document.querySelector(
    "#editpolicyscriptdialog .modal-body",
  )
  modalbody.innerHTML = ""

  // find the td with the input fields from the clicked script
  const inputWrapper =
    clickedElement.parentElement.parentElement.previousElementSibling

  // loop over all input fields, and render them in the modal
  inputWrapper
    .querySelectorAll(".policy-script-param")
    .forEach((inputparam, index) => {
      const paramType = getFieldType(inputparam.getAttribute("data-inputtype"))
      let newElement

      if (paramType == "textfield") {
        newElement = document.createElement("select")

        /* defaultValues will be 'None' if we come directly from adding a new script.
         This is because the values are taken from django template variable "params",
         which will only be #PARAMS# when we come directly from adding a new script */
        let options
        if (defaultValues != "None") {
          options = defaultValues[index].split(",")
        } else {
          options = inputparam.getAttribute("default_value").split(",")
        }
        for (let o of options) {
          o = o.trim()
          let optionElement = document.createElement("option")
          optionElement.innerHTML = o
          optionElement.value = o
          newElement.appendChild(optionElement)
        }
      } else {
        newElement = document.createElement("input")
      }

      if (paramType == "file") {
        /* In principle, it'd be nice (for display purposes) to copy the
         FileList from the hidden input into the modal dialog -- but
         this confuses Firefox 65 enormously, and when we try to copy
         the FileList back again, it gets cleared! */
        newElement.files = inputparam.files
      } else {
        if (paramType == "checkbox") {
          newElement.checked = inputparam.value === "True" ? true : false
        }
        newElement.value = inputparam.value
      }

      // set the commen attributes type, name, id, class
      newElement.type = paramType
      newElement.name = "edit_" + inputparam.getAttribute("name")
      newElement.id = "edit_" + inputparam.getAttribute("name")
      newElement.className =
        paramType !== "checkbox"
          ? "form-control"
          : "form-control form-check-input"

      // Create a label element
      let label = inputparam.nextElementSibling.querySelector(
        ".policy-script-print-name",
      )
      let labelElement = document.createElement("label")
      labelElement.setAttribute("for", newElement.id)
      labelElement.textContent = label.textContent

      modalbody.appendChild(labelElement)
      modalbody.appendChild(newElement)
    })

  editModal.modal("show")
}

function submitEditDialog(policy_id) {
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

    if (inputField.required == true) {
      if (
        inputElement.type == "file" &&
        inputElement.files.length == 0 &&
        inputField.files.length == 0
      ) {
        /* If the hidden input field has a value, then it's fine if
           this one doesn't -- we won't overwrite it */
        inputElement.classList.add("invalid")
        return false
      } else if (inputElement.value.trim().length == 0) {
        inputElement.classList.add("invalid")
        return false
      }
    }

    inputElement.classList.remove("invalid")
    count += 1
  })

  if (count != modalInputs.length) {
    return false
  }

  // loop over inputs inside the modal, and set their corresponding hidden input fields in the group form
  modalInputs.forEach((inputElement) => {
    let inputName = inputElement.getAttribute("name").substring(5)
    let inputField = wrapper.querySelector('input[name="' + inputName + '"]')

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

    if (inputElement.getAttribute("type") === "file") {
      if (inputElement.files.length !== 0) {
        inputField.files = inputElement.files
        visibleValueField.textContent = inputElement.files[0].name
      }
    } else if (inputElement.getAttribute("type") === "checkbox") {
      inputField.value = inputElement.checked ? "True" : "False"
      visibleValueField.innerHTML =
        '<input type="checkbox" class="form-check-input" disabled ' +
        (inputElement.checked ? "checked>" : ">")
    } else if (inputElement.getAttribute("type") === "password") {
      inputField.value = inputElement.value
      visibleValueField.textContent = "•••••"

      // This workaround prevents the browser from prompting to save a password
      inputElement.setAttribute("type", "text")
      inputElement.setAttribute("style", "display: none;")
      const clonedElement = inputElement.cloneNode()
      inputElement.parentElement.appendChild(clonedElement)
      inputElement.remove()
    } else {
      inputField.value = inputElement.value
      visibleValueField.textContent = inputElement.value
    }
  })

  $("#editpolicyscriptdialog").modal("hide")
  return false
}

function getFieldType(type) {
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

function updateNew(id) {
  let count = 0
  let inputs = document.querySelectorAll("#" + id + " input.policy-script-pos")

  inputs.forEach((inputElement) => {
    let parentElement = inputElement.parentElement

    if (inputElement.value.match(/^new_/)) {
      parentElement
        .querySelector("input.policy-script-name")
        .setAttribute("name", id + "_new_" + count)
      let params = parentElement.querySelectorAll("input.policy-script-param")

      params.forEach((param, index) => {
        param.setAttribute("name", id + "_new_" + count + "_param_" + index)
      })

      inputElement.value = "new_" + count
      count++
    }

    document.getElementById(id + "_new_entries").value = count
  })
}

function removeItem(clickedElem, id) {
  // Find the closest parent <tr> element
  const rowElement = clickedElem.closest("tr")

  if (rowElement) {
    rowElement.remove()
  }

  updateNew(id)
}
