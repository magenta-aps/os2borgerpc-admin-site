from unicodedata import category

from system.models import SettingsCategory, SubSettingsCategory
from django.views.generic import RedirectView, CreateView

from system.forms import SettingsCategoryForm, SubSettingsCategoryForm
from system.views_dir.utils.helper_views import SiteView
from system.mixins.views_mixins import SiteMixin
from django.urls import reverse
from django.views.generic.base import RedirectView
from django.shortcuts import get_object_or_404


class SettingsCategoriesRedirect(RedirectView, SiteMixin):
    def get_redirect_url(self, *args, **kwargs):
        first_category = SettingsCategory.objects.order_by("title").first()

        return reverse(
            "pc_setting_category",
            kwargs={
                "slug": kwargs["slug"],
                "category": first_category.title if first_category.title else "new",
            },
        )


class SettingsCategories(SiteMixin, SiteView):
    template_name = "system/pc_management_page/settings_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = SettingsCategory.objects.order_by("title").all()
        context["sub_categories"] = SubSettingsCategory.objects.all()
        context["sub_categories"] = SubSettingsCategory.objects.filter(
            category__title=self.kwargs["category"]
        ).order_by("title")
        context["current_category"] = self.kwargs["category"]
        # Only include the form if needed
        if self.request.user.is_superuser:
            context["category_form"] = SettingsCategoryForm()
            context["sub_category_form"] = SubSettingsCategoryForm()
        print("The context is:", context)
        return context


class SettingsCategoryCreate(SiteMixin, CreateView):
    form_class = SettingsCategoryForm

    def get_success_url(self):
        slug = self.kwargs["slug"]
        category = self.kwargs["category"]
        return reverse(
            "pc_setting_category", kwargs={"slug": slug, "category": category}
        )


class SettingsCategoriesSpecific(SiteView, SiteMixin):
    template_name = "system/pc_management_page/settings_detail_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class SubSettingsCategoryCreate(SiteMixin, CreateView):
    form_class = SubSettingsCategoryForm

    def dispatch(self, request, *args, **kwargs):
        # Validate category from URL before proceeding to form handling
        print("The category in dispatch:", self.kwargs["category"])
        self.category = get_object_or_404(
            SettingsCategory, title=self.kwargs["category"]
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.category = self.category
        print("Assigned category:", self.category)
        print("Form instance before save:", form.instance.__dict__)
        return super().form_valid(form)

    def get_success_url(self):
        slug = self.kwargs["slug"]
        category = self.kwargs["category"]
        return reverse(
            "pc_setting_category", kwargs={"slug": slug, "category": category}
        )
