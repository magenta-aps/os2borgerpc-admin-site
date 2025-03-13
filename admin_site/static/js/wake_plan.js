const WEEK_PLAN = document.getElementById("week-plan")
const WAKE_PLAN_FROM_URL_KEY = "last_plan_id"

// Turns a week day on/off
// If off start_time and end_time are hidden. If on required is set to true, to remove the browser x button to clear the time field
function weekDayOn(el, on) {
  const START_TIME = el.parentElement.parentElement.children[3]
  const START_TIME_INPUT =
    el.parentElement.parentElement.children[3].firstElementChild
  const SEPARATOR = el.parentElement.parentElement.children[4]
  const END_TIME = el.parentElement.parentElement.children[5]
  const END_TIME_INPUT =
    el.parentElement.parentElement.children[5].firstElementChild
  const ON_OFF_TEXT =
    el.parentElement.parentElement.children[2].firstElementChild

  if (on) {
    START_TIME.style.visibility = "visible"
    START_TIME_INPUT.setAttribute("required", true)
    SEPARATOR.style.visibility = "visible"
    END_TIME.style.visibility = "visible"
    END_TIME_INPUT.setAttribute("required", true)
    ON_OFF_TEXT.innerText = gettext("On")
  } else {
    START_TIME.style.visibility = "hidden"
    START_TIME_INPUT.removeAttribute("required")
    SEPARATOR.style.visibility = "hidden"
    END_TIME.style.visibility = "hidden"
    END_TIME_INPUT.removeAttribute("required")
    ON_OFF_TEXT.innerText = gettext("Off")
  }
}

// Handling the week plan switches
function checkboxOpenCloseHandler(event) {
  const TG = event.target

  if (TG.type == "checkbox") {
    if (TG.checked) {
      weekDayOn(TG, true)
    } else if (!TG.checked) {
      weekDayOn(TG, false)
    }
  }
}

WEEK_PLAN.addEventListener("click", checkboxOpenCloseHandler)

// By default all dates are seen as "on" - this toggles those off to off for the week plan
for (let day of WEEK_PLAN.tBodies[0].children) {
  const checkbox = day.getElementsByClassName("checkbox")[0]
  if (!checkbox.checked) {
    weekDayOn(checkbox, false)
  } else {
    weekDayOn(checkbox, true)
  }
}

const CHECKBOX_ENABLED = document.getElementById("id_enabled")
const CHECKBOX_ENABLED_LABEL = document.getElementById("id_enabled_label")
if (CHECKBOX_ENABLED) {
  // Don't attempt to set this listener if we're on a subpage where this doesn't exist
  function setPlanStateText(on) {
    if (on) {
      CHECKBOX_ENABLED_LABEL.innerText = gettext("Active")
    } else CHECKBOX_ENABLED_LABEL.innerText = gettext("Inactive")
  }

  CHECKBOX_ENABLED.addEventListener("click", function () {
    if (CHECKBOX_ENABLED.checked) setPlanStateText(true)
    else setPlanStateText(false)
  })
}

// TODO: If a new wakechangeevent is saved, set a cookie with its ID and name, and then this page could have a focus listener that add it to the picklist as an option?

// Store current plan_id in SessionStorage
sessionStorage.setItem(WAKE_PLAN_FROM_URL_KEY, location.href)


// Serialize current wake plan, save it to session storage
function saveInputStates() {
  sessionStorage.setItem(
    "wake_plan_settings",
    JSON.stringify(getWakePlanSettingsAsJSON()),
  )
  sessionStorage.setItem("going_to_wake_change_events", "true")
}

// Serialise the current week plan state to JSON (relevant if there are unsaved changes), done before saving it to session storage
// This does not handle saving the picklists
function getWakePlanSettingsAsJSON() {
  const wakePlanSettingsAsJSON = {}
  document.querySelectorAll(".json-input").forEach(element => {
    if (element.type === "checkbox"){
      wakePlanSettingsAsJSON[element.name ?? element.id] = element.checked
    }
    else if (element.nodeName === "SPAN"){
      wakePlanSettingsAsJSON[element.name ?? element.id] = element.textContent
    }
    else {
      wakePlanSettingsAsJSON[element.name ?? element.id] = element.value
    }
  })

  return wakePlanSettingsAsJSON
}

// Restore a wake plan after returning from wake change event
function runWhenReturnedToPage() {
  const wakePlanSettingsAsJSON = JSON.parse(
    sessionStorage.getItem("wake_plan_settings"),
  )

  const nodes =   document.querySelectorAll(".json-input")
  nodes.forEach(element => {
    if (element.type === "checkbox"){
      element.checked = wakePlanSettingsAsJSON[element.name ?? element.id]
    }
    else if (element.nodeName === "SPAN"){
     element.textContent =  wakePlanSettingsAsJSON[element.name ?? element.id]
    }
    else {
       element.value = wakePlanSettingsAsJSON[element.name ?? element.id]
    }
  })
}

// When returning to the wake plan restore the state and ...?
if (sessionStorage.getItem("going_back_to_wake_plan") === "true") {
  sessionStorage.setItem("going_back_to_wake_plan", "false")
  runWhenReturnedToPage()
}

sessionStorage.setItem("going_to_wake_change_events", "false")

document.querySelectorAll(".wake_change_events_link").forEach(element =>  element.addEventListener("click", saveInputStates))

document.addEventListener("beforeunload", (evt) => {
  if (sessionStorage.getItem("going_to_wake_change_events") !== "true") {
    removeDataFromSessionStorage()
  }
})

// A function to clear the session storage storing what a wake plan looks like to be able to navigate to wake
// change events from a wake plan without losing wake plan state
function removeDataFromSessionStorage() {
  sessionStorage.setItem("going_to_wake_change_events", "false")

  sessionStorage.setItem("going_back_to_wake_plan", "false")

  sessionStorage.setItem("wake_plan_settings", "{}")

  sessionStorage.setItem(
    "wake_plan_wake_change_events_user_has_made_changes_to_options",
    "false",
  )
  sessionStorage.setItem("wake_plan_wake_change_events_options", "[]")

  sessionStorage.setItem(
    "wake_plan_groups_user_has_made_changes_to_options",
    "false",
  )
  sessionStorage.setItem("wake_plan_groups_options", "[]")
}

document
  .getElementById("submit-button")
  .addEventListener("click", () => {
    removeDataFromSessionStorage()
  })

document
  .getElementById("cancel-button")
  .addEventListener("click", () => {
    removeDataFromSessionStorage()
    location.reload(true) // true means it reloads from server, false will reload from cache
  })

// Limitation: Doesn't currently detect changes in picklists! Also it prevents "Gem ændringer" and going to Wake Change Events, which isn't great
// TODO is considering whether this should be added, in some edited form, to all pages in the future, fx. by adding it to custom.js
// Credit: https://stackoverflow.com/a/57069660
// 'use strict'
// (() => {
//   const modified_inputs = new Set()
//   const defaultValue = 'defaultValue'
//   // store default values
//   addEventListener('beforeinput', evt => {
//     const target = evt.target
//     if (!(defaultValue in target.dataset)) {
//       target.dataset[defaultValue] = ('' + (target.value || target.textContent)).trim()
//     }
//   })
//
//   // detect input modifications
//   addEventListener('input', evt => {
//     const target = evt.target
//     let original = target.dataset[defaultValue]
//
//     let current = ('' + (target.value || target.textContent)).trim()
//
//     if (original !== current) {
//       if (!modified_inputs.has(target)) {
//         modified_inputs.add(target)
//       }
//     } else if (modified_inputs.has(target)) {
//       modified_inputs.delete(target)
//     }
//   })
//
//   addEventListener(
//     'saved',
//     function(e) {
//       modified_inputs.clear()
//     },
//     false
//   )
//
//   addEventListener('beforeunload', evt => {
//     if (modified_inputs.size) {
//       const unsaved_changes_warning = 'Ændringer du har lavet er ikke blevet gemt.'
//       evt.returnValue = unsaved_changes_warning
//       return unsaved_changes_warning
//     }
//   })
//
// })()