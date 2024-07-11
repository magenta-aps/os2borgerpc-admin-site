from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.db import transaction

import account.models as m

admin.site.unregister(User)

# INLINES #


class UserProfileInline(admin.TabularInline):
    model = m.UserProfile
    readonly_fields = (
        "id",
        "sites",
    )
    show_change_link = True
    extra = 0

    def sites(self, obj):
        return obj.sites.values_list("name")


class SiteMembershipInline(admin.TabularInline):
    model = m.SiteMembership
    extra = 0


# ADMIN OVERRIDES #


@admin.register(User)
class MyUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = (
        "username",
        "email",
        "last_login",
        "sites",
        "is_staff",
        "is_active",
        "user_profile",
    )
    search_fields = ("username", "email")

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not hasattr(obj, "user_profile"):
            m.UserProfile.objects.create(user=obj)

    def sites(self, obj):
        return list(obj.user_profile.sites.all())


@admin.register(m.UserProfile)
class MyUserProfileAdmin(admin.ModelAdmin):
    inlines = [SiteMembershipInline]
    list_display = ("user", "user_sites", "language")
    list_filter = ("sites",)
    search_fields = ("user__username",)

    def user_sites(self, obj):
        return list(obj.sites.all())
