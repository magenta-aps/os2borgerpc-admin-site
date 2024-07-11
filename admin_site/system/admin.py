from hashlib import md5
import os

from django.contrib import admin
from django.db.models import Count
from django.utils import timezone
from django.utils.html import format_html_join, escape, mark_safe
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from system.models import (
    APIKey,
    AssociatedScript,
    AssociatedScriptParameter,
    Batch,
    BatchParameter,
    Citizen,
    Configuration,
    ConfigurationEntry,
    Customer,
    FeaturePermission,
    ImageVersion,
    Input,
    Job,
    LoginLog,
    EventRuleServer,
    Product,
    PC,
    PCGroup,
    Script,
    ScriptTag,
    SecurityEvent,
    SecurityProblem,
    Site,
    WakeChangeEvent,
    WakeWeekPlan,
    Country,
)

from changelog.models import (
    Changelog,
    ChangelogComment,
    ChangelogTag,
)


# Note FileFields are created with a name set to "#" - this sets them to empty strings, so we can distinguish the two scenarios.
# Ie. to exclude images which never had a multilang image ("#") from those that did (""). Ideally None would be used for one of these, but FileFields doesn't handle None correctly.
@admin.action(
    description=_(
        "Remove image file references and delete them from disk (keeps the ImageVersion object)"
    )
)
def delete_images(modeladmin, request, queryset):
    for image_version in queryset:
        if image_version.image_upload:
            try:
                os.remove(image_version.image_upload.path)
            except FileNotFoundError:
                pass
        if image_version.image_upload_multilang:
            try:
                os.remove(image_version.image_upload_multilang.path)
            except FileNotFoundError:
                pass
    queryset.update(image_upload=None, image_upload_multilang=None)


class ConfigurationEntryInline(admin.TabularInline):
    model = ConfigurationEntry
    extra = 0


class SiteInlineForConfiguration(admin.TabularInline):
    model = Site
    extra = 0

    def has_change_permission(self, request, obj):
        return False


class PCGroupInline(admin.TabularInline):
    model = PCGroup
    extra = 0

    def has_change_permission(self, request, obj):
        return False


class PCInlineForConfiguration(admin.TabularInline):
    model = PC
    extra = 0

    def has_change_permission(self, request, obj):
        return False


class ConfigurationAdmin(admin.ModelAdmin):
    def sites(self, obj):
        return list(obj.site_set.all())

    def pcgroups(self, obj):
        return list(obj.pcgroup_set.all())

    def pcs(self, obj):
        return list(obj.pc_set.all())

    list_display = ["id", "name", "pcs", "pcgroups", "sites"]
    search_fields = (
        "id",
        "name",
    )
    inlines = [
        ConfigurationEntryInline,
        SiteInlineForConfiguration,
        PCGroupInline,
        PCInlineForConfiguration,
    ]


class PCInline(admin.TabularInline):
    model = PC.pc_groups.through
    extra = 0

    def has_change_permission(self, request, obj):
        return False


class AssociatedScriptInline(admin.TabularInline):
    model = AssociatedScript
    extra = 0

    def has_change_permission(self, request, obj):
        return False

    def has_add_permission(self, request, obj):
        return False


class PCGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "site")
    list_filter = ("site",)
    inlines = [PCInline, AssociatedScriptInline]


class BatchParameterAdmin(admin.ModelAdmin):
    readonly_fields = ("input", "batch")


class JobInline(admin.TabularInline):
    fields = ("id", "pc", "status", "user", "created", "started", "finished")
    readonly_fields = ("id", "pc", "status", "user", "created", "started", "finished")
    model = Job
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj):
        return False


class BatchParameterInline(admin.TabularInline):
    model = BatchParameter
    extra = 0
    readonly_fields = ("input",)


class BatchAdmin(admin.ModelAdmin):
    list_display = ("id", "site", "name", "script")
    fields = ("site", "name", "script")
    list_filter = ("site",)
    search_fields = ("name", "site__name", "script__name")
    readonly_fields = ("script",)
    inlines = [JobInline, BatchParameterInline]


class InputInline(admin.TabularInline):
    model = Input
    extra = 0

    def has_change_permission(self, request, obj):
        return False


class ScriptAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_global",
        "is_security_script",
        "is_hidden",
        "site",
        "jobs_per_site",
        "jobs_per_site_for_the_last_year",
        "associations_to_groups_per_site",
        "uid",
        "executable_code",
    )
    filter_horizontal = ("tags",)
    readonly_fields = ("user_created", "user_modified")
    search_fields = ("name", "executable_code")
    inlines = [InputInline]

    def is_global(self, obj):
        return obj.is_global

    is_global.boolean = True
    is_global.short_description = _("Global")
    is_global.admin_order_field = "site"

    def jobs_per_site(self, obj):
        sites = Site.objects.filter(batches__script=obj).annotate(
            num_jobs=Count("batches__jobs")
        )

        return format_html_join(
            "\n", "<p>{} - {}</p>", ([(site.name, site.num_jobs) for site in sites])
        )

    jobs_per_site.short_description = _("Jobs per site")

    def jobs_per_site_for_the_last_year(self, obj):
        now = timezone.now()
        a_year_ago = now - timezone.timedelta(days=365)

        sites = Site.objects.filter(
            batches__script=obj, batches__jobs__started__gte=a_year_ago
        ).annotate(num_jobs=Count("batches__jobs"))

        return format_html_join(
            "\n", "<p>{} - {}</p>", ([(site.name, site.num_jobs) for site in sites])
        )

    jobs_per_site_for_the_last_year.short_description = _(
        "Jobs per Site for the last year"
    )

    def associations_to_groups_per_site(self, obj):
        sites = Site.objects.all()
        pairs = []
        for site in sites:
            count = AssociatedScript.objects.filter(
                script=obj.id, group__site=site.id
            ).count()
            if count > 0:
                pairs.append(tuple((site, count)))

        return format_html_join(
            "\n", "<p>{} - {}</p>", ([(pair[0], pair[1]) for pair in pairs])
        )


class FeaturePermissionInlineForCustomerAdmin(admin.TabularInline):
    model = FeaturePermission.customers.through
    extra = 0


class SiteInlineForCustomerAdmin(admin.TabularInline):
    model = Site
    fields = ("name", "uid")
    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj):
        return False


class CustomerAdmin(admin.ModelAdmin):
    list_filter = ("country",)
    list_display = (
        "name",
        "is_test",
        "number_of_computers",
        "number_of_borgerpc_computers",
        "number_of_kioskpc_computers",
        "paid_for_access_until",
        "feature_permissions",
        "sites",
    )
    search_fields = ("name",)
    inlines = (
        SiteInlineForCustomerAdmin,
        FeaturePermissionInlineForCustomerAdmin,
    )

    def sites(self, obj):
        return list(obj.sites.all())

    def number_of_computers(self, obj):
        computers_count = PC.objects.filter(site__customer=obj).count()
        return computers_count

    def number_of_borgerpc_computers(self, obj):
        borgerpc_computers_count = (
            PC.objects.filter(site__in=obj.sites.all())
            .filter(configuration__entries__value="os2borgerpc")
            .count()
        )

        return borgerpc_computers_count

    def number_of_kioskpc_computers(self, obj):
        kioskpc_computers_count = (
            PC.objects.filter(site__in=obj.sites.all())
            .filter(configuration__entries__value="os2borgerpc kiosk")
            .count()
        )

        return kioskpc_computers_count

    def feature_permissions(self, obj):
        return list(obj.feature_permission.all())

    number_of_computers.short_description = _("Number of computers")
    feature_permissions.short_description = _("Feature permissions")
    number_of_kioskpc_computers.short_description = _("Number of KioskPC computers")
    number_of_borgerpc_computers.short_description = _("Number of BorgerPC computers")


class PCInlineForSiteAdmin(admin.TabularInline):
    model = PC
    fields = ("name", "uid")
    readonly_fields = ("name", "uid")
    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False


class SiteAdmin(admin.ModelAdmin):
    list_filter = ("customer",)
    list_display = (
        "name",
        "uid",
        "created",
        "number_of_computers",
        "number_of_borgerpc_computers",
        "number_of_kioskpc_computers",
    )
    search_fields = ("name",)
    inlines = (PCInlineForSiteAdmin,)
    readonly_fields = ("created",)

    def number_of_borgerpc_computers(self, obj):
        borgerpc_computers_count = (
            PC.objects.filter(site=obj)
            .filter(configuration__entries__value="os2borgerpc")
            .count()
        )

        return borgerpc_computers_count

    def number_of_kioskpc_computers(self, obj):
        kioskpc_computers_count = (
            PC.objects.filter(site=obj)
            .filter(configuration__entries__value="os2borgerpc kiosk")
            .count()
        )

        return kioskpc_computers_count

    def number_of_computers(self, obj):
        return obj.pcs.count()

    number_of_computers.short_description = _("Number of computers")


class LoginLogAdmin(admin.ModelAdmin):
    list_display = ("identifier", "date", "login_time", "logout_time")
    list_filter = ("date",)
    search_fields = ("identifier", "date")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(site__in=request.user.user_profile.sites.all())


class FeaturePermissionAdmin(admin.ModelAdmin):
    def customers_with_access(self, obj):
        return list(obj.customers.all())

    list_display = (
        "name",
        "uid",
        "customers_with_access",
    )
    list_filter = ("name",)
    search_fields = ("name", "uid")

    customers_with_access.short_description = _("customers with access")


class PCAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "uid",
        "site_link",
        "is_activated",
        "last_seen",
        "created",
        "os2borgerpc_client_version",
    )
    list_filter = (
        "site",
        "is_activated",
    )
    search_fields = ("name", "uid")
    readonly_fields = ("created", "configuration")

    def site_link(self, obj):
        link = reverse("admin:system_site_change", args=[obj.site_id])
        return mark_safe(f'<a href="{link}">{escape(obj.site.__str__())}</a>')

    def os2borgerpc_client_version(self, obj):
        return obj.configuration.get("_os2borgerpc.client_version")

    site_link.short_description = _("Site")
    site_link.admin_order_field = "site"

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request,
            queryset,
            search_term,
        )
        # PC UID is generated from a hashed MAC address
        # so by hashing the input we allow searching by MAC address.
        maybe_uid_hash = md5(search_term.encode("utf-8").lower()).hexdigest()
        queryset |= self.model.objects.filter(uid=maybe_uid_hash)
        return queryset, may_have_duplicates


class JobAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "status",
        "user",
        "pc",
        "created",
        "started",
        "finished",
    )
    list_filter = ("status",)
    search_fields = ("batch__script__name", "user__username", "pc__name")
    readonly_fields = ("created", "started", "finished", "batch", "pc")


class CustomerInlineForCountryAdmin(admin.TabularInline):
    model = Customer
    fields = ("name", "is_test")
    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj):
        return False


class CountryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "pk",
    )
    list_filter = ("name",)
    search_fields = ("name", "pk")
    inlines = [CustomerInlineForCountryAdmin]


class ScriptTagAdmin(admin.ModelAdmin):
    pass


class ImageVersionAdmin(admin.ModelAdmin):
    list_display = ("product", "image_version", "os", "release_date")
    actions = [delete_images]


class SecurityProblemAdmin(admin.ModelAdmin):
    list_display = ("name", "site", "level", "security_script")


class EventRuleServerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "site",
        "level",
        "monitor_period_start",
        "monitor_period_end",
        "maximum_offline_period",
    )


class SecurityEventAdmin(admin.ModelAdmin):
    list_display = (
        "problem",
        "event_rule_server",
        "get_site",
        "occurred_time",
        "reported_time",
        "pc",
        "status",
    )
    search_fields = ("pc__site__name", "problem__name", "pc__name", "status")
    list_filter = (
        ("problem__security_script", admin.RelatedOnlyFieldListFilter),
        ("occurred_time", admin.DateFieldListFilter),
        ("reported_time", admin.DateFieldListFilter),
        "status",
        "pc__site",
    )
    readonly_fields = ("problem", "event_rule_server", "pc")

    @admin.display(description="Site", ordering="pc__site")
    def get_site(self, obj):
        return obj.pc.site


class AssociatedScriptParameterInline(admin.TabularInline):
    model = AssociatedScriptParameter
    extra = 0
    readonly_fields = ("input",)


class AssociatedScriptAdmin(admin.ModelAdmin):
    list_display = ("script", "get_site", "group", "position")
    search_fields = ("script__name",)
    readonly_fields = ("script", "group", "position")
    inlines = [AssociatedScriptParameterInline]

    @admin.display(description="Site", ordering="group__site")
    def get_site(self, obj):
        return obj.group.site


class AssociatedScriptParameterAdmin(admin.ModelAdmin):
    list_display = (
        "associated_script",
        "input",
        "string_value",
        "file_value",
        "get_site",
    )
    search_fields = ("associated_script__script__name",)
    readonly_fields = ("input", "associated_script")

    @admin.display(description="Site", ordering="associated_script__group__site")
    def get_site(self, obj):
        return obj.associated_script.group.site


class CitizenAdmin(admin.ModelAdmin):
    list_display = ("citizen_id", "last_successful_login", "site")
    search_fields = ("citizen_id",)


class ChangelogAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "published",
        "created",
        "updated",
    )
    search_fields = ("title",)
    filter_horizontal = ("tags",)


class ChangelogTagAdmin(admin.ModelAdmin):
    pass


class ChangelogCommentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "created",
        "changelog",
        "content",
    )
    readonly_fields = (
        "created",
        "user",
        "parent_comment",
        "changelog",
    )


class WakeWeekPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "enabled",
        "site",
        "sleep_state",
        "monday_on",
        "monday_off",
        "tuesday_on",
        "tuesday_off",
        "wednesday_on",
        "wednesday_off",
        "thursday_on",
        "thursday_off",
        "friday_on",
        "friday_off",
        "saturday_on",
        "saturday_off",
        "sunday_on",
        "sunday_off",
    )
    inlines = [PCGroupInline]
    filter_horizontal = ("wake_change_events",)
    list_filter = ("site",)
    search_fields = ("name",)


class WakeWeekPlanInline(admin.TabularInline):
    model = WakeWeekPlan.wake_change_events.through
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False


class WakeChangeEventAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "type",
        "date_start",
        "date_end",
        "time_start",
        "time_end",
        "site",
    )
    inlines = [WakeWeekPlanInline]
    list_filter = ("site",)


class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("site", "key", "description", "created")


class ImageVersionInline(admin.TabularInline):
    model = ImageVersion
    extra = 0

    # Just show the image versions, no need to have them editable from here
    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ProductAdmin(admin.ModelAdmin):
    inlines = [ImageVersionInline]


ar = admin.site.register

ar(APIKey, APIKeyAdmin)
ar(AssociatedScript, AssociatedScriptAdmin)
ar(AssociatedScriptParameter, AssociatedScriptParameterAdmin)
ar(Batch, BatchAdmin)
ar(BatchParameter, BatchParameterAdmin)
ar(Changelog, ChangelogAdmin)
ar(ChangelogComment, ChangelogCommentAdmin)
ar(ChangelogTag, ChangelogTagAdmin)
ar(Citizen, CitizenAdmin)
ar(Configuration, ConfigurationAdmin)
ar(Country, CountryAdmin)
ar(Customer, CustomerAdmin)
ar(EventRuleServer, EventRuleServerAdmin)
ar(FeaturePermission, FeaturePermissionAdmin)
ar(ImageVersion, ImageVersionAdmin)
ar(Job, JobAdmin)
ar(LoginLog, LoginLogAdmin)
ar(PC, PCAdmin)
ar(PCGroup, PCGroupAdmin)
ar(Product, ProductAdmin)
ar(Script, ScriptAdmin)
ar(ScriptTag, ScriptTagAdmin)
ar(SecurityEvent, SecurityEventAdmin)
ar(SecurityProblem, SecurityProblemAdmin)
ar(Site, SiteAdmin)
ar(WakeChangeEvent, WakeChangeEventAdmin)
ar(WakeWeekPlan, WakeWeekPlanAdmin)
