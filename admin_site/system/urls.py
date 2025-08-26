from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from django.views.i18n import JavaScriptCatalog
from system.views import (
    AdminIndex,
    APIKeyCreate,
    APIKeyDelete,
    APIKeyUpdate,
    ConfigurationEntryCreate,
    ConfigurationEntryUpdate,
    FileArchive,
    FileArchiveCreate,
    FileArchiveDelete,
    GlobalScriptRedirect,
    ImageVersionRedirect,
    ImageVersionRedirectSite,
    ImageVersionView,
    JobInfo,
    JobRestarter,
    JobSearch,
    JobsView,
    GlobalJobsViewRedirect,
    PCGroupCreate,
    PCGroupDelete,
    PCGroupDuplicate,
    PCGroupRedirect,
    PCGroupUpdate,
    PCsOverview,
    PCsOverviewTable,
    PCDelete,
    PCUpdate,
    PCUpdateRedirect,
    ScriptCreate,
    ScriptDelete,
    ScriptRedirect,
    ScriptRun,
    ScriptUpdate,
    SecurityEventSearch,
    SecurityEventsUpdate,
    SecurityEventsView,
    SecurityProblemCreate,
    SecurityProblemDelete,
    SecurityProblemUpdate,
    EventRuleRedirect,
    GlobalEventRuleRedirect,
    EventRuleServerCreate,
    EventRuleServerDelete,
    EventRuleServerUpdate,
    SiteDashboardJobListUpdate,
    SiteDashboardView,
    SiteList,
    SiteCreate,
    SiteUIDAvailableCheck,
    SiteDelete,
    SiteSettings,
    TwoFactor,
    UserCreate,
    UserDelete,
    UserLink,
    UserRedirect,
    UserRedirectSite,
    UserUpdate,
    WakeChangeEventCreate,
    WakeChangeEventDelete,
    WakeChangeEventRedirect,
    WakeChangeEventUpdate,
    WakePlanCreate,
    WakePlanDelete,
    WakePlanDuplicate,
    WakePlanRedirect,
    WakePlanUpdate,
)

urlpatterns = [
    # TODO: Switch to using the django javascript translation system
    # For translations of strings in javascript files that are printed to the user
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    # Security events UI
    path(
        "site/<slug>/security_events/update/",
        SecurityEventsUpdate.as_view(),
        name="security_events_update",
    ),
    path(
        "site/<slug>/security_events/search/",
        SecurityEventSearch.as_view(),
        name="security_event_search",
    ),
    path(
        "site/<slug>/security_events/",
        SecurityEventsView.as_view(),
        name="security_events",
    ),
    # Shared by Security Problems and Event Rule Servers
    path(
        "site/<slug>/event_rules/",
        EventRuleRedirect.as_view(),
        name="event_rules",
    ),
    # To be able to link here for anonymous users from e.g. e-mails/PDFs
    path(
        "event_rules/",
        GlobalEventRuleRedirect.as_view(),
        name="event_rules_redirect",
    ),
    # Security problems
    path(
        "site/<slug>/security_problems/new/",
        SecurityProblemCreate.as_view(),
        name="event_rule_security_problem_new",
    ),
    path(
        "site/<slug>/security_problems/<int:id>/delete/",
        SecurityProblemDelete.as_view(),
        name="event_rule_security_problem_delete",
    ),
    path(
        "site/<slug>/security_problems/<int:id>/",
        SecurityProblemUpdate.as_view(),
        name="event_rule_security_problem",
    ),
    # Event Rule Server
    path(
        "site/<slug>/event_rules_server/new/",
        EventRuleServerCreate.as_view(),
        name="event_rule_server_new",
    ),
    path(
        "site/<slug>/event_rules_server/<int:id>/delete/",
        EventRuleServerDelete.as_view(),
        name="event_rule_server_delete",
    ),
    path(
        "site/<slug>/event_rules_server/<int:id>/",
        EventRuleServerUpdate.as_view(),
        name="event_rule_server",
    ),
    # Security scripts
    path(
        "site/<slug>/security_scripts/<int:script_pk>)/delete/",
        ScriptDelete.as_view(is_security=True),
        name="security_script_delete",
    ),
    path(
        "site/<slug>/security_scripts/<int:script_pk>/",
        ScriptUpdate.as_view(is_security=True),
        name="security_script",
    ),
    path(
        "site/<slug>/security_scripts/new/",
        ScriptCreate.as_view(is_security=True),
        name="new_security_script",
    ),
    path(
        "site/<slug>/security_scripts/",
        ScriptRedirect.as_view(),
        name="security_scripts",
    ),
    # Two-factor for OS2borgerPC machines
    path("site/<slug>/two-factor/", TwoFactor.as_view(), name="two_factor"),
    # Sites
    path("", AdminIndex.as_view(), name="index"),
    path("sites/", SiteList.as_view(), name="sites"),
    path(
        "sites/new/",
        SiteCreate.as_view(),
        name="site_create",
    ),
    path(
        "site/<slug>/delete/",
        SiteDelete.as_view(),
        name="site_delete",
    ),
    path("site/<slug>/", SiteDashboardView.as_view(), name="dashboard"),
    # Site Settings
    path("site/<slug>/settings/", SiteSettings.as_view(), name="settings"),
    path(
        "site/<slug>/configuration/new/",
        ConfigurationEntryCreate.as_view(),
        name="new_configuration",
    ),
    path(
        "site/<slug>/configuration/edit/<int:pk>/",
        ConfigurationEntryUpdate.as_view(),
        name="edit_configuration",
    ),
    # Computers
    path(
        "site/<slug>/status/",
        PCsOverview.as_view(),
        name="computers_overview",
    ),
    path(
        "site/<slug>/computers/",
        PCUpdateRedirect.as_view(),
        name="computers",
    ),
    path(
        "site/<slug>/computers/<pc_uid>/",
        PCUpdate.as_view(),
        name="computer",
    ),
    path(
        "site/<slug>/computers/<pc_uid>/delete/",
        PCDelete.as_view(),
        name="computer_delete",
    ),
    # Groups
    path("site/<slug>/groups/", PCGroupRedirect.as_view(), name="groups"),
    path(
        "site/<slug>/groups/new/",
        PCGroupCreate.as_view(),
        name="new_group",
    ),
    path(
        "site/<slug>/groups/<int:group_id>/",
        PCGroupUpdate.as_view(),
        name="group",
    ),
    path(
        "site/<slug>/groups/<int:group_id>/delete/",
        PCGroupDelete.as_view(),
        name="group_delete",
    ),
    path(
        "site/<slug>/groups/<int:group_id>/duplicate/",
        PCGroupDuplicate.as_view(),
        name="group_duplicate",
    ),
    # Wake Plans
    path(
        "site/<slug>/wake_plans/",
        WakePlanRedirect.as_view(),
        name="wake_plans",
    ),
    # This URL needs to be above WakePlanUpdate, as otherwise that regex tries to parse the word "new" as an ID
    path(
        "site/<slug>/wake_plan/new/",
        WakePlanCreate.as_view(),
        name="wake_plan_new",
    ),
    path(
        "site/<slug>/wake_plan/<int:wake_week_plan_id>/",
        WakePlanUpdate.as_view(),
        name="wake_plan",
    ),
    path(
        "site/<slug>/wake_plan/<int:wake_week_plan_id>/delete/",
        WakePlanDelete.as_view(),
        name="wake_plan_delete",
    ),
    path(
        "site/<slug>/wake_plan/<int:wake_week_plan_id>/duplicate/",
        WakePlanDuplicate.as_view(),
        name="wake_plan_duplicate",
    ),
    # Wake Change Events
    path(
        "site/<slug>/wake_change_events/",
        WakeChangeEventRedirect.as_view(),
        name="wake_change_events",
    ),
    # This URL needs to be above WakeChangeEventUpdate, as otherwise that regex tries to parse the word "new" as an ID
    path(
        "site/<slug>/wake_change_event/new_altered_hours/",
        WakeChangeEventCreate.as_view(),
        name="wake_change_event_new_altered_hours",
    ),
    path(
        "site/<slug>/wake_change_event/new_closed/",
        WakeChangeEventCreate.as_view(),
        name="wake_change_event_new_closed",
    ),
    path(
        "site/<slug>/wake_change_event/<int:wake_change_event_id>/",
        WakeChangeEventUpdate.as_view(),
        name="wake_change_event",
    ),
    path(
        "site/<slug>/wake_change_event/<int:wake_change_event_id>/delete/",
        WakeChangeEventDelete.as_view(),
        name="wake_change_event_delete",
    ),
    # Jobs
    path("site/<slug>/jobs/search/", JobSearch.as_view(), name="jobsearch"),
    path(
        "site/<slug>/jobs/<int:pk>/restart/",
        JobRestarter.as_view(),
        name="restart_job",
    ),
    path(
        "site/<slug>/jobs/<int:pk>/info/",
        JobInfo.as_view(),
        name="job_info",
    ),
    path("site/<slug>/jobs/", JobsView.as_view(), name="jobs"),
    # To be able to link here for anonymous users from e.g. e-mails/PDFs
    path("jobs/", GlobalJobsViewRedirect.as_view(), name="jobs_redirect"),
    # Scripts
    path(
        "site/<slug>/scripts/<int:script_pk>/delete/",
        ScriptDelete.as_view(),
        name="script_delete",
    ),
    path(
        "site/<slug>/scripts/<int:script_pk>/run/",
        ScriptRun.as_view(),
        name="run_script",
    ),
    path(
        "site/<slug>/scripts/<int:script_pk>/",
        ScriptUpdate.as_view(),
        name="script",
    ),
    path("site/<slug>/scripts/new/", ScriptCreate.as_view(), name="new_script"),
    path("site/<slug>/scripts/", ScriptRedirect.as_view(), name="scripts"),
    # To be able to link here for anonymous users from e.g. e-mails/PDFs
    path(
        "scripts/<int:script_pk>/",
        GlobalScriptRedirect.as_view(),
        name="script_redirect_id",
    ),
    path(
        "scripts/uid/<script_uid>/",
        GlobalScriptRedirect.as_view(),
        name="script_redirect_uid",
    ),
    # Users
    path("site/<slug>/users/", UserRedirect.as_view(), name="users"),
    path("users/", UserRedirectSite.as_view(), name="users_redirect_site"),
    path("site/<slug>/users/new/", UserCreate.as_view(), name="new_user"),
    path("site/<slug>/users/link/", UserLink.as_view(), name="link_users"),
    path(
        "site/<slug>/users/<username>/",
        UserUpdate.as_view(),
        name="user",
    ),
    path(
        "site/<slug>/users/<username>/delete/",
        UserDelete.as_view(),
        name="user_delete",
    ),
    # Documentation
    path(
        "documentation/os2borgerpc_installation_guide/",
        RedirectView.as_view(url=static("docs/OS2BorgerPC_installation_guide_da.pdf")),
    ),
    # Image Versions
    path(
        "site/<slug>/image-versions/",
        ImageVersionRedirect.as_view(),
        name="images",
    ),
    path(
        "image-versions/",
        ImageVersionRedirectSite.as_view(),
        name="images-redirect-site",
    ),
    path(
        "site/<slug>/image-versions/<int:product_id>/",
        ImageVersionView.as_view(),
        name="images-product",
    ),
    # Files
    path(
        "site/<slug>/file_archive/",
        FileArchive.as_view(),
        name="file_archive",
    ),
    path(
        "site/<slug>/file_archive/new/",
        FileArchiveCreate.as_view(),
        name="file_archive_new",
    ),
    path(
        "site/<slug>/file_archive/<int:pk>/update/",
        FileArchive.as_view(),
        name="file_archive_update",
    ),
    path(
        "site/<slug>/file_archive/<int:pk>/delete/",
        FileArchiveDelete.as_view(),
        name="file_archive_delete",
    ),
    # API Key
    # This contains both a regular view and an HTMX view
    path(
        "site/<slug>/api-keys/",
        APIKeyUpdate.as_view(),
        name="api_keys",
    ),
]

# Define HTMX URL Patterns here, and add them to the urlpatterns list
# Basically these are views that only return partial HTML fragments rather than entire pages
htmx_urlpatterns = [
    # API Key
    path(
        "site/<slug>/api-keys/new/",
        APIKeyCreate.as_view(),
        name="api_key_new",
    ),
    path(
        "site/<slug>/api-key/<int:pk>/update/",
        APIKeyUpdate.as_view(),
        name="api_key_update",
    ),
    path(
        "site/<slug>/api-key/<int:pk>/delete/",
        APIKeyDelete.as_view(),
        name="api_key_delete",
    ),
    path(
        "site/<slug>/dashboard/update/",
        SiteDashboardJobListUpdate.as_view(),
        name="dashboard_jobs",
    ),
    # Sites overview
    path(
        "sites/new-validate/",
        SiteUIDAvailableCheck.as_view(),
        name="site_uid_available_check",
    ),
    # Computers overview table
    path(
        "site/<slug>/status/table",
        PCsOverviewTable.as_view(),
        name="computers_overview_table",
    ),
]

urlpatterns += htmx_urlpatterns
