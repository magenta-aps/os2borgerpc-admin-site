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
class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = (
        "username",
        "email",
        "customer",
        "sites",
        "user_profile",
        "language",
        "totp_enabled",
        "is_active",
        "is_staff",
        "is_superuser",
        "last_login",
    )
    list_filter = (
        "user_profile__sites",
        "user_profile__sites__customer",
        ("totpdevice", admin.EmptyFieldListFilter),
        "is_active",
        "is_superuser",
        ("is_staff", admin.BooleanFieldListFilter),
    )
    search_fields = ("username", "email")

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not hasattr(obj, "user_profile"):
            m.UserProfile.objects.create(user=obj)

    @admin.display(ordering="user_profile__sites__customer")
    def customer(self, obj):
        if obj.user_profile.sites.count() > 0:
            return obj.user_profile.sites.first().customer

    @admin.display(ordering="user_profile__sites")
    def sites(self, obj):
        return list(obj.user_profile.sites.all())

    @admin.display(description="2FA active", ordering="totpdevice", boolean=True)
    def totp_enabled(self, obj):
        return bool(obj.totpdevice_set.count())

    @admin.display(ordering="user_profile.language")
    def language(self, obj):
        return obj.user_profile.get_language_display()


@admin.register(m.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    inlines = [SiteMembershipInline]
    list_display = ("user",)
    search_fields = ("user__username",)
