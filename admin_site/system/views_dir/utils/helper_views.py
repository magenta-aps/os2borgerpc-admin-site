from django.views.generic import DetailView
from system.models import (
    SecurityEvent,
    Site,
)
from system.mixins.views_mixins import SuperAdminOrThisSiteMixin


# Base class for Site-based passive (non-form) views_dir
class SiteView(DetailView, SuperAdminOrThisSiteMixin):
    """Base class for all views_dir based on a single site."""

    model = Site
    slug_field = "uid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site = self.get_object()
        # Add information about outstanding security events.
        no_of_sec_events = SecurityEvent.objects.priority_events_for_site(site).count()
        context["sec_events"] = no_of_sec_events

        return context
