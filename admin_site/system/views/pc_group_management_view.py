# -*- coding: utf-8 -*-

from django.urls import reverse

from django.views.generic import RedirectView
from system.views.utils.helper_views import SiteView
from system.mixins.views_mixins import SiteMixin


class SettingsCategoriesRedirect(RedirectView, SiteMixin):
    def get_redirect_url(self, *args, **kwargs):
        # chosen_category = modelName.objects.getFirst()
        return reverse(
            "pc_setting_category",
            kwargs={"slug": kwargs["slug"], "category": "browser"},
        )

class SettingsCategories(SiteView, SiteMixin):
    template_name = "system/pc_settings_page/settings_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

class SettingsCategoriesSpecific(SiteView, SiteMixin):
    template_name = "system/pc_settings_page/settings_detail_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
