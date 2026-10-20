import re

from django.conf import settings
from django.urls import reverse
from django.contrib.staticfiles.finders import find
from markdownx.utils import markdownify

from system.models import Script


DELIMITER = "€€"


# NOTE: Currently appends STATIC_ROOT in front to prevent whitenoise from creating a manifest and referencing that which results in ugly URLs.
# An alternative solution would be to serve these as media files instead of static files, or letting a webserver serve them.
def get_doc_user_lang(file_path, extension, user_lang):
    """Get the document in the user's language if available - otherwise fall back to danish."""
    file_path = f"{file_path}_{user_lang}{extension}"
    fallback_language = "da"

    if find(file_path):
        return settings.STATIC_ROOT + "/" + file_path
    else:
        return (
            settings.STATIC_ROOT
            + "/"
            + file_path.replace(user_lang + extension, fallback_language + extension)
        )


def render_custom_links(text, site_uid, also_markdownify):
    """Used on plaintext to create dynamic links elsewhere that stay on the current site.

    The fallbacks are only relevant in places where the UID can't be obtained.
    Specifically in the changelog if one isn't visiting it from the admin site (REFERER is not the admin site)

    Prefer the more specific redirect for a link and only fall back to the global one (SITE) if
    a specific one hasn't been added yet, because this means less URL hardcoding.

    The redirects to e.g. specific scripts could actually parse the ID and get the URL
    to that specific script, but then it would fail in rendering if it doesn't exist, so currently
    it's just a link to the section.
    An improvement would be to use that ID for the paths, and then have a fallback that stays on the same site.
    Only when a site can't be identified, the global redirects are used.
    """

    index = 0
    while True:
        match = re.search(f"{DELIMITER}[a-z_]+/?[0-9a-z_]*", text[index:])
        if not match:
            break

        index = match.start()
        m = match.group()
        # For links to specific objects, that include /something. Can currently be a PK or a Script UID.
        identifier = 1
        try:
            res = m.split("/")[1]
            if res:
                identifier = res
        except Exception:
            pass
        replacement = ""
        # site_uid indicates whether it's an anonymous user (e.g. changelog in some cases) or not
        if "site" in m:
            if site_uid:
                replacement = reverse("dashboard", args=[site_uid])
            else:
                replacement = reverse("index")
        elif "event_rules" in m:
            if site_uid:
                replacement = reverse("event_rules", args=[site_uid])
            else:
                replacement = reverse("event_rules_redirect")
        elif "jobs" in m:
            if site_uid:
                replacement = reverse("jobs", args=[site_uid])
            else:
                replacement = reverse("jobs_redirect")
        elif "sec_script/" in m:  # This check needs to be before SCRIPT
            if site_uid:
                replacement = reverse("security_script", args=[site_uid, identifier])
            else:
                replacement = reverse("script_redirect_id", args=[identifier])
        elif "script/" in m:
            if site_uid:
                replacement = reverse("script", args=[site_uid, identifier])
            else:
                replacement = reverse("script_redirect_id", args=[identifier])
        elif "scriptn/" in m or "scriptnu/" in m:
            if "scriptnu/" in m:
                identifier = (
                    Script.objects.filter(uid=identifier, site=None)
                    .values_list("pk", flat=True)
                    .first()
                )
            if site_uid:
                addr = reverse("script", args=[site_uid, identifier])
            else:
                addr = reverse("script_redirect_id", args=[identifier])
            script_name = (
                Script.objects.filter(pk=identifier, site=None)
                .values_list("name", flat=True)
                .first()
            )
            if script_name:
                replacement = f"[{script_name}]({addr})"

        text = text.replace(m, replacement)

    if also_markdownify:
        # Turn markdown into HTML
        text = markdownify(text)

    return text
