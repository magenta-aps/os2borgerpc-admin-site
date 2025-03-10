document.addEventListener('DOMContentLoaded', (event) => {
    // Run highlight js on all code tags
    for (const code of document.getElementsByTagName("code")) {
        hljs.highlightElement(code)
    }

    // Support linking to specific changelog entries, shown in modals
    path = window.location.pathname
    regex = /.*\/(\d+)\/$/
    match = path.match(regex)
    if (match !== null && typeof match[1] !== undefined) {
        changelogModalId = "changelogDetails-" + match[1]
        new bootstrap.Modal(document.getElementById(changelogModalId)).show()
    }
})

function toggleCommentForm(pk) {
    replyForm = document.getElementById("reply-form-" + pk)
    toggleButton = document.getElementById("reply-toggle-button-" + pk)

    replyForm.style.display = replyForm.style.display == "none" ? "block" : "none"
    toggleButton.style.display = replyForm.style.display == "none" ? "block" : "none"
}

function toggleCommentChildren(pk, children) {
    commentChildren = document.getElementById("comment-children-" + pk)
    toggleButton = document.getElementById("comment-children-toggle-button-" + pk)

    commentChildren.style.display = commentChildren.style.display == "none" ? "block" : "none"
    toggleButton.innerText = commentChildren.style.display == "block" ? "Gem svar" : "Vis " + children + " svar"
}
