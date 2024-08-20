import os

from django.views.generic import View, TemplateView
from django.http import Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator


# Mixin class to require login
class LoginRequiredMixin(View):
    """Subclass in all views where login is required."""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class DocView(TemplateView, LoginRequiredMixin):
    docname = "status"

    def template_exists(self, subpath):
        fullpath = os.path.join(settings.INSTALL_DIR + "/docs/templates/", subpath)
        return os.path.isfile(fullpath)

    def get_context_data(self, **kwargs):  # noqa

        user_lang = self.request.user.user_profile.language

        documentation_menu_items = [
            ("", _("The administration site")),
            ("om_os2borgerpc_admin", _("About")),
            ("sites_overview", _("Sites overview")),
            ("status", _("Status")),
            ("computers", _("Computers")),
            ("groups", _("Groups")),
            ("wake_plans", _("On/Off schedules")),
            ("jobs", _("Jobs")),
            ("scripts", _("Scripts")),
            ("security_scripts", _("Security Scripts")),
            ("notifications", _("Notifications and offline rules")),
            ("users", _("Users")),
            ("configuration", _("Configurations")),
            ("changelogs", _("The News site")),
            ("api", "API"),
            (
                "docs/OS2BorgerPC_security_rules_" + user_lang + ".pdf",
                _("Setting up security surveillance (PDF)"),
            ),
            ("", _("OS2borgerPC")),
            (
                "docs/OS2BorgerPC_installation_guide_" + user_lang + ".pdf",
                _("Installation Guide (PDF)"),
            ),
            (
                "docs/OS2BorgerPC_installation_guide_old_" + user_lang + ".pdf",
                _("Old installation guide (PDF)"),
            ),
            ("", _("OS2borgerPC Kiosk")),
            (
                "https://os2borgerpc-server-image.readthedocs.io/en/latest/install_setup.html",
                _("Installation Guide"),
            ),
            ("os2borgerpc_kiosk_wifi_guide", _("Updating Wi-Fi setup")),
            ("", _("Audit")),
            ("docs/Audit_doc_" + user_lang + ".pdf", _("FAQ (PDF)")),
            ("", _("Technical Documentation")),
            ("https://os2borgerpc-image.readthedocs.io", _("OS2borgerPC Image")),
            ("https://os2borgerpc-admin.readthedocs.io", _("OS2borgerPC Admin Site")),
            (
                "https://os2borgerpc-server-image.readthedocs.io",
                _("OS2borgerPC Kiosk Image"),
            ),
            ("https://os2borgerpc-client.readthedocs.io", _("OS2borgerPC Client")),
        ]

        if "name" in self.kwargs:
            self.docname = self.kwargs["name"]
        else:
            # This will be mapped to documentation/index.html
            self.docname = "index"

        if self.docname.find("..") != -1:
            raise Http404

        # Try <docname>.html and <docname>/index.html
        name_templates = ["{0}.html", "{0}/index.html"]

        templatename = None
        for nt in name_templates:
            expanded = nt.format(self.docname)
            if self.template_exists(expanded):
                templatename = expanded
                break

        if templatename is None:
            raise Http404
        else:
            self.template_name = templatename

        context = super(DocView, self).get_context_data(**kwargs)
        context["docmenuitems"] = documentation_menu_items
        docnames = self.docname.split("/")

        # Returns the first site the user is a member of
        context["site"] = self.request.user.user_profile.sites.first()

        context["menu_active"] = docnames[0]

        # Set heading according to chosen item
        current_heading = None
        for link, name in context["docmenuitems"]:
            if link == "":
                current_heading = name
            elif link == docnames[0]:
                context["docheading"] = current_heading
                break

        # Add a submenu if it exists
        submenu_template = docnames[0] + "/__submenu__.html"
        if self.template_exists(submenu_template):
            context["submenu_template"] = submenu_template

        if len(docnames) > 1 and docnames[1]:
            # Don't allow direct access to submenus
            if docnames[1] == "__submenu__":
                raise Http404
            context["submenu_active"] = docnames[1]

        params = self.request.GET or self.request.POST
        back_link = params.get("back")
        if back_link is None:
            referer = self.request.META.get("HTTP_REFERER")
            if referer and referer.find("/documentation/") == -1:
                back_link = referer
        if back_link:
            context["back_link"] = back_link

        return context
