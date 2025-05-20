from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator


from django.views.generic import View

from system.models import (
    SecurityEvent,
    Site,
)


# Mixin class for CRUD views_dir that use site_uid in URL
# The "site_uid" slug is configurable, but please avoid clashes
class SiteMixin(View):
    """Mixin class to extract site UID from URL"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site = get_object_or_404(Site, uid=self.kwargs["slug"])
        context["site"] = site
        # Add information about outstanding security events.
        no_of_sec_events = SecurityEvent.objects.priority_events_for_site(site).count()
        context["sec_events"] = no_of_sec_events

        return context


# Mixin class to require login
class LoginRequiredMixin(View):
    """Subclass in all views_dir where login is required."""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class SuperAdminOnlyMixin(LoginRequiredMixin):
    """Only allows access to super admins."""

    check_function = user_passes_test(lambda u: u.is_superuser, login_url="/")

    @method_decorator(login_required)
    @method_decorator(check_function)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class SuperAdminOrThisSiteMixin(LoginRequiredMixin):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """Limit access to super users or users belonging to THIS site."""
        site = None
        slug_field = None
        # Check if a site slug is included in the url
        if "slug" in kwargs:
            slug_field = "slug"
        # If none given, give up
        if slug_field:
            try:
                site = Site.objects.get(uid=kwargs["slug"])
            except Site.DoesNotExist:
                return redirect("/")
        check_function = user_passes_test(
            lambda u: (u.is_superuser) or (site and site in u.user_profile.sites.all()),
            login_url="/",
        )
        wrapped_super = check_function(super().dispatch)
        return wrapped_super(*args, **kwargs)


# Mixin class for list selection (single select).
class SelectionMixin(View):
    """This supplies the ability to highlight a selected object of a given
    class. This is useful if a Detail view contains a list of children which
    the user is allowed to select."""

    # The Python class of the Django model corresponding to the objects you
    # want to be able to select. MUST be specified in subclass.
    selection_class = None
    # A callable which will return a list of objects which SHOULD belong to the
    # class specified by selection_class. MUST be specified in subclass.
    get_list = None
    # The field which is used to look up the selected object.
    lookup_field = "uid"
    # Overrides the default class name in context.
    class_display_name = None

    def get_context_data(self, **kwargs):
        # First, call superclass
        context = super().get_context_data(**kwargs)
        # Then get selected object, if any
        if self.lookup_field in self.kwargs:
            lookup_val = self.kwargs[self.lookup_field]
            lookup_params = {self.lookup_field: lookup_val}
            selected = get_object_or_404(self.selection_class, **lookup_params)
        else:
            selected = self.get_list()[0] if self.get_list() else None

        display_name = (
            self.class_display_name
            if self.class_display_name
            else self.selection_class.__name__.lower()
        )
        if selected is not None:
            context["selected_{0}".format(display_name)] = selected
        context["{0}_list".format(display_name)] = self.get_list()
        return context


class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(self.get_data(context), **response_kwargs)

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context
