import re

from django.urls import reverse

from markdownx.utils import markdownify

DELIMITER = "€€"


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
        match = re.search(f"{DELIMITER}[A-Z_]+/?[0-9]*", text[index:])
        if not match:
            break

        index = match.start()
        m = match.group()
        # For links to specific objects, that include /something
        id = 1
        try:
            res = m.split("/")[1]
            if res:
                id = res
        except Exception:
            pass
        # site_uid indicates whether it's an anonymous user (e.g. changelog in some cases) or not
        if "SITE" in m:
            if site_uid:
                replacement = reverse("dashboard", args=[site_uid])
            else:
                replacement = reverse("index")
        elif "EVENT_RULES" in m:
            if site_uid:
                replacement = reverse("event_rules", args=[site_uid])
            else:
                replacement = reverse("event_rules_redirect")
        elif "JOBS" in m:
            if site_uid:
                replacement = reverse("jobs", args=[site_uid])
            else:
                replacement = reverse("jobs_redirect")
        elif "SEC_SCRIPT/" in m:  # This check needs to be before SCRIPT
            if site_uid:
                replacement = reverse("security_script", args=[site_uid, id])
            else:
                replacement = reverse("script_redirect_id", args=[id])
        elif "SCRIPT/" in m:
            if site_uid:
                replacement = reverse("script", args=[site_uid, id])
            else:
                replacement = reverse("script_redirect_id", args=[id])
        text = text.replace(m, replacement)

    if also_markdownify:
        # Turn markdown into HTML
        text = markdownify(text)

    return text
