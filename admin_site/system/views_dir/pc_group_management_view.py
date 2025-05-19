from system.models import SettingsCategory, SubSettingsCategory
from django.views.generic import RedirectView, CreateView

from system.forms import SettingsCategoryForm
from system.views_dir.utils.helper_views import SiteView
from system.mixins.views_mixins import SiteMixin
from django.urls import reverse
from django.views.generic.base import RedirectView


class SettingsCategoriesRedirect(RedirectView, SiteMixin):
    def get_redirect_url(self, *args, **kwargs):
        first_category = SettingsCategory.objects.order_by('title').first()

        if not first_category:
            return "/"  # fallback if empty

        return reverse(
            "pc_setting_category",  # your url name
            kwargs={
                "slug": kwargs["slug"],  # e.g., "magenta"
                "category": first_category.title,  # e.g., "Browser"
            },
        )

class SettingsCategories( SiteMixin, CreateView):
    template_name = "system/pc_settings_page/settings_list.html"
    form_class = SettingsCategoryForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = SettingsCategory.objects.all()
        context["sub_category"] = SubSettingsCategory.objects.filter()
        context["slug"] = self.kwargs["slug"]
        return context

    def get_success_url(self):
        slug = self.kwargs.get("slug")
        category = self.kwargs.get("category")
        return reverse("pc_setting_category", kwargs={"slug": slug, "category": category})

class SettingsCategoriesSpecific(SiteView, SiteMixin):
    template_name = "system/pc_management_page/settings_detail_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
