from django.contrib.auth.models import User, Permission
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.forms import Form

from django.views.generic import RedirectView
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    FormView,
    UpdateView,
)

import django_otp
from two_factor.forms import TOTPDeviceForm
from two_factor.utils import default_device
from two_factor import views as otp_views
from two_factor.plugins.phonenumber.utils import get_available_phone_methods
from django_otp.decorators import otp_required
from django_otp import devices_for_user, user_has_device
from django_otp.plugins.otp_static.models import StaticToken

from system.views import LoginRequiredMixin, SuperAdminOrThisSiteMixin
from account.models import SiteMembership, UserProfile
from system.models import SecurityEvent, Site


from account.forms import (
    UserForm,
    UserFormSSO,
    UserLinkForm,
)

from system.utils import (
    get_notification_string,
    set_notification_cookie,
)


def otp_check(
    view=None, redirect_field_name="next", login_url=None, if_configured=False
):
    """
    Modfied version of otp_required that redirects to site root if you do not have a device configured
    The normal version redirects to the login page, which results in a loop of logging in,
    hitting a url that requires otp and being redirected back to login
    """
    if login_url is None:
        login_url = "/"

    def test(user):
        return user.is_verified() or (
            if_configured and user.is_authenticated and not user_has_device(user)
        )

    decorator = user_passes_test(
        test, login_url=login_url, redirect_field_name=redirect_field_name
    )

    return decorator if (view is None) else decorator(view)


class UserRedirect(RedirectView, SuperAdminOrThisSiteMixin):
    """Redirects to either an existing user if one exists, or to the create user page"""

    def get_redirect_url(self, **kwargs):
        site = get_object_or_404(Site, uid=kwargs["slug"])
        users_on_site = site.users
        if users_on_site.exists():
            if self.request.user in users_on_site:
                destination_user = self.request.user.username
            else:  # for superusers just go to the first user in the list
                destination_user = users_on_site.first().username

            return reverse(
                "user", kwargs={"slug": site.uid, "username": destination_user}
            )

        else:
            return reverse("new_user", args=[site.uid])


# To be able to link all customers to the users page with a single link
class UserRedirectSite(RedirectView, LoginRequiredMixin):
    def get_redirect_url(self, **kwargs):
        slug = self.request.user.user_profile.sites.first().uid
        return reverse("users", kwargs={"slug": slug})


class UsersMixin(object):
    def add_site_to_context(self, context):
        self.site = get_object_or_404(Site, uid=self.kwargs["slug"])
        context["site"] = self.site
        return context

    def add_userlist_to_context(self, context):
        if "site" not in context:
            self.add_site_to_context(context)
        if self.request.user.is_superuser:
            context["user_list"] = context["site"].users
        elif self.request.user.user_profile.is_hidden:
            context["user_list"] = context["site"].users.filter(is_superuser=False)
        else:
            context["user_list"] = context["site"].users.filter(
                user_profile__is_hidden=False, is_superuser=False
            )
        if (
            not self.request.user.is_superuser
            and not self.request.user.user_profile.sitemembership_set.filter(
                site_user_type=SiteMembership.CUSTOMER_ADMIN
            )
        ):
            context["user_list"] = context["user_list"].exclude(
                user_profile__sitemembership__site_user_type=SiteMembership.CUSTOMER_ADMIN
            )
        # Add information about outstanding security events.
        no_of_sec_events = SecurityEvent.objects.priority_events_for_site(
            self.site
        ).count()
        context["sec_events"] = no_of_sec_events
        return context

    def add_membership_to_context(self, context):
        if "user_list" not in context:
            self.add_userlist_to_context(context)
        request_user = self.request.user
        user_profile = request_user.user_profile
        site_membership = user_profile.sitemembership_set.filter(
            site=context["site"]
        ).first()

        if site_membership:
            loginusertype = site_membership.site_user_type
        else:
            loginusertype = 0
        if not context["site"].customer.using_sso:
            context["form"].setup_usertype_choices(
                loginusertype, request_user.is_superuser
            )

        context["site_membership"] = site_membership
        return context


class UserLink(FormView, UsersMixin, SuperAdminOrThisSiteMixin):
    form_class = UserLinkForm
    template_name = "system/users/link.html"

    def get(self, request, *args, **kwargs):
        """
        Overwrite the get method to ensure that non-customer
        admins can't directly access the UserLink URL.
        """
        site = get_object_or_404(Site, uid=self.kwargs["slug"])

        if (
            not self.request.user.is_superuser
            and self.request.user.user_profile.sitemembership_set.get(
                site=site
            ).site_user_type
            != SiteMembership.CUSTOMER_ADMIN
        ):
            raise PermissionDenied
        response = super().get(request, *args, **kwargs)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.add_membership_to_context(context)

        site = context["site"]
        form = context["form"]

        # user list related
        user_profiles_for_customer_pk = site.customer.sites.values_list(
            "user_profiles", flat=True
        )
        # Limit the possible selections to users for this customer that
        # do not already have access to this site
        users_for_customer_not_on_this_site = User.objects.filter(
            user_profile__pk__in=user_profiles_for_customer_pk
        ).exclude(user_profile__sites=site)
        form.fields["linkable_users"].queryset = users_for_customer_not_on_this_site

        return context

    def form_valid(self, form):
        site = get_object_or_404(Site, uid=self.kwargs["slug"])
        # Ensure that only customer admins can use this functionality
        if (
            not self.request.user.is_superuser
            and self.request.user.user_profile.sitemembership_set.get(
                site=site
            ).site_user_type
            != SiteMembership.CUSTOMER_ADMIN
        ):
            raise PermissionDenied
        selected_users = form.cleaned_data["linkable_users"].filter(
            user_profile__sitemembership__site__customer=site.customer
        )
        selected_user_type = form.cleaned_data["usertype"]
        selected_users_names = []
        # Add the selected users to the site with
        # the selected user type
        for user in selected_users:
            selected_users_names.append(user.username)
            SiteMembership.objects.create(
                user_profile=user.user_profile,
                site=site,
                site_user_type=selected_user_type,
            )
        response = super().form_valid(form)

        if selected_users_names:
            added_users_string = get_notification_string(selected_users_names)
            set_notification_cookie(
                response,
                _("The user(s) %s have been added to the site %s ")
                % (
                    added_users_string,
                    site.name,
                ),
            )

        return response

    def get_success_url(self):
        return reverse(
            "link_users",
            kwargs={
                "slug": self.kwargs["slug"],
            },
        )


class UserCreate(CreateView, UsersMixin, SuperAdminOrThisSiteMixin):
    model = User
    form_class = UserForm
    template_name = "system/users/update.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["language"] = self.request.user.user_profile.language
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.add_membership_to_context(context)
        return context

    def form_valid(self, form):
        site = get_object_or_404(Site, uid=self.kwargs["slug"])
        site_membership = self.request.user.user_profile.sitemembership_set.filter(
            site=site
        ).first()

        if self.request.user.is_superuser:
            site_membership = self.request.user.user_profile.sitemembership_set.first()

        if (
            self.request.user.is_superuser
            or site_membership.site_user_type >= site_membership.SITE_ADMIN
            and site_membership.site_user_type >= int(form.cleaned_data["usertype"])
        ):
            self.object = form.save()
            user_profile = UserProfile.objects.create(user=self.object)
            # If a customer admin user is being created, ensure that
            # they have access to all sites for this customer
            if int(form.cleaned_data["usertype"]) == SiteMembership.CUSTOMER_ADMIN:
                for customer_site in site.customer.sites.all():
                    SiteMembership.objects.create(
                        user_profile=user_profile,
                        site=customer_site,
                        site_user_type=form.cleaned_data["usertype"],
                    )
            # If a non-customer admin user is being created,
            # only give them access to this site
            else:
                SiteMembership.objects.create(
                    user_profile=user_profile,
                    site=site,
                    site_user_type=form.cleaned_data["usertype"],
                )
            user_profile.language = form.cleaned_data["language"]
            user_profile.save()
            if int(
                form.cleaned_data["usertype"]
            ) >= site_membership.SITE_ADMIN and site.customer.feature_permission.filter(
                uid__in=["quria", "sms-login"]
            ):
                self.object.user_permissions.set(
                    Permission.objects.filter(name="Can view login log")
                )
                self.object.is_staff = True
            result = super().form_valid(form)
            return result
        else:
            raise PermissionDenied

    def get_success_url(self):
        return reverse(
            "user",
            kwargs={
                "slug": self.kwargs["slug"],
                "username": self.object.username,
            },
        )


class UserUpdate(UpdateView, UsersMixin, SuperAdminOrThisSiteMixin):
    model = User
    template_name = "system/users/update.html"

    # SSO user form is a lot simpler and only has a single field in the form, so conditionally set which form is used based on whether sso is set
    def get_form(self, form_class=None):
        site = get_object_or_404(Site, uid=self.kwargs["slug"])

        if site.customer.using_sso:
            form_class = UserFormSSO
        else:
            form_class = UserForm

        return super().get_form(form_class)

    def get_object(self, queryset=None):
        try:
            self.selected_user = User.objects.get(username=self.kwargs["username"])
            selected_user_site_membership = (
                self.selected_user.user_profile.sitemembership_set.get(
                    site__uid=self.kwargs["slug"]
                )
            )
        except (User.DoesNotExist, SiteMembership.DoesNotExist):
            raise Http404(
                _("You have no user with the following username: %s")
                % self.kwargs["username"]
            )
        if (
            selected_user_site_membership.site_user_type
            == SiteMembership.CUSTOMER_ADMIN
            and not self.request.user.user_profile.sitemembership_set.filter(
                site_user_type=SiteMembership.CUSTOMER_ADMIN
            )
            or self.selected_user.is_superuser
            or self.selected_user.user_profile.is_hidden
            and not self.request.user.user_profile.is_hidden
        ) and not self.request.user.is_superuser:
            raise PermissionDenied

        return self.selected_user

    def get_context_data(self, **kwargs):
        # This line is necessary, as without it UserUpdate will think that user = selected_user
        self.context_object_name = "selected_user"
        context = super().get_context_data(**kwargs)
        self.add_membership_to_context(context)

        context["customer_using_sso"] = context["site"].customer.using_sso

        context["selected_user"] = User.objects.get(username=self.kwargs["username"])

        context["selected_user_site_membership"] = context[
            "selected_user"
        ].user_profile.sitemembership_set.get(site=context["site"])

        if context["selected_user"].user_profile.sitemembership_set.filter(
            site_user_type=SiteMembership.CUSTOMER_ADMIN
        ):
            context["not_customer_admin"] = False
        else:
            context["not_customer_admin"] = True

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        site = get_object_or_404(Site, uid=self.kwargs["slug"])
        kwargs["site"] = site

        return kwargs

    def form_valid(self, form):
        site = get_object_or_404(Site, uid=self.kwargs["slug"])
        site_membership_req_user = (
            self.request.user.user_profile.sitemembership_set.filter(site=site).first()
        )
        if (
            self.request.user.is_superuser
            or site_membership_req_user.site_user_type
            >= site_membership_req_user.SITE_ADMIN
            or self.request.user == self.selected_user
        ):
            user_profile = self.object.user_profile
            site_membership = user_profile.sitemembership_set.get(
                site=site, user_profile=user_profile
            )
            requested_user_type = int(
                form.cleaned_data.get("usertype") or site_membership.site_user_type
            )

            if (
                not self.request.user.is_superuser
                and requested_user_type > site_membership_req_user.site_user_type
            ):
                raise PermissionDenied

            self.object = form.save()

            # If a user was made a customer admin, ensure that they have access
            # to all sites for this customer
            if (
                site_membership.site_user_type != requested_user_type
                and requested_user_type == SiteMembership.CUSTOMER_ADMIN
            ):
                for customer_site in site.customer.sites.all():
                    try:
                        customer_site_membership = user_profile.sitemembership_set.get(
                            site=customer_site
                        )
                        customer_site_membership.site_user_type = requested_user_type
                        customer_site_membership.save()
                    except SiteMembership.DoesNotExist:
                        SiteMembership.objects.create(
                            user_profile=user_profile,
                            site=customer_site,
                            site_user_type=requested_user_type,
                        )
            # If a customer admin was changed to a less privileged user type,
            # update all their site memberships to reflect this
            elif (
                site_membership.site_user_type != requested_user_type
                and site_membership.site_user_type == SiteMembership.CUSTOMER_ADMIN
            ):
                for customer_site_membership in user_profile.sitemembership_set.filter(
                    site__customer=site.customer
                ):
                    customer_site_membership.site_user_type = requested_user_type
                    customer_site_membership.save()
            else:
                site_membership.site_user_type = requested_user_type
                site_membership.save()
            if (
                not self.selected_user.is_superuser
                and not self.selected_user.user_profile.is_hidden
                and requested_user_type >= site_membership.SITE_ADMIN
                and site.customer.feature_permission.filter(
                    uid__in=["quria", "sms-login"]
                )
            ):
                self.object.user_permissions.set(
                    Permission.objects.filter(name="Can view login log")
                )
                self.object.is_staff = True
            elif (
                not self.selected_user.is_superuser
                and not self.selected_user.user_profile.is_hidden
                and requested_user_type < site_membership.SITE_ADMIN
                and site.customer.feature_permission.filter(
                    uid__in=["quria", "sms-login"]
                )
                and all(
                    user_type < site_membership.SITE_ADMIN
                    for user_type in self.selected_user.user_profile.sitemembership_set.exclude(
                        site=site
                    ).values_list("site_user_type", flat=True)
                )
            ):
                self.object.is_staff = False
            user_profile.language = form.cleaned_data["language"]
            user_profile.save()
            response = super().form_valid(form)
            set_notification_cookie(
                response, _("User %s updated") % self.object.username
            )
            return response
        else:
            raise PermissionDenied

    def get_success_url(self):
        return reverse(
            "user",
            kwargs={
                "slug": self.kwargs["slug"],
                "username": self.object.username,
            },
        )


class UserDelete(DeleteView, UsersMixin, SuperAdminOrThisSiteMixin):
    model = User
    template_name = "system/users/confirm_delete.html"

    def get_object(self, queryset=None):
        try:
            self.selected_user = User.objects.get(username=self.kwargs["username"])
            site_membership = self.selected_user.user_profile.sitemembership_set.get(
                site__uid=self.kwargs["slug"]
            )
        except (User.DoesNotExist, SiteMembership.DoesNotExist):
            raise Http404(
                _("You have no user with the following username: %s")
                % self.kwargs["username"]
            )
        request_user_type = self.request.user.user_profile.sitemembership_set.get(
            site__uid=self.kwargs["slug"]
        ).site_user_type
        if (
            site_membership.site_user_type == SiteMembership.CUSTOMER_ADMIN
            or request_user_type < site_membership.SITE_ADMIN
            or self.selected_user.is_superuser
            or self.selected_user.user_profile.is_hidden
            and not self.request.user.user_profile.is_hidden
        ) and not self.request.user.is_superuser:
            raise PermissionDenied
        return self.selected_user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.add_userlist_to_context(context)
        context["selected_user"] = self.selected_user

        return context

    def get_success_url(self):
        return reverse("users", kwargs={"slug": self.kwargs["slug"]})

    def form_valid(self, form, *args, **kwargs):
        site = get_object_or_404(Site, uid=self.kwargs["slug"])
        # If the selected_user is a member of multiple sites, only remove them from this site
        if len(self.object.user_profile.sitemembership_set.all()) > 1:
            self.object.user_profile.sitemembership_set.get(site_id=site.id).delete()
            response = redirect(self.get_success_url())
            set_notification_cookie(
                response,
                _("User %s removed from the site %s")
                % (self.kwargs["username"], site.name),
            )
        else:
            response = super().delete(form, *args, **kwargs)
            set_notification_cookie(
                response, _("User %s deleted") % self.kwargs["username"]
            )
        return response


class LoginView(otp_views.LoginView):
    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)

        if self.request.resolver_match.url_name == "sso-login-error":
            context["sso_login_error"] = True

        return context


class AdminTwoFactorDisable(otp_views.DisableView, SuperAdminOrThisSiteMixin):
    form_class = Form

    def get_success_url(self):
        return reverse(
            "user",
            kwargs={
                "slug": self.kwargs["slug"],
                "username": self.kwargs["username"],
            },
        )

    def get_context_data(self, **kwargs):
        site = get_object_or_404(Site, uid=self.kwargs["slug"])
        context = {"site": site, "user": self.request.user, "form": Form}
        return context

    def dispatch(self, *args, **kwargs):
        """This function has been overwritten to make it use get_success_url
        and to redirect when the username does not match"""
        # If the username in the url doesn't match request.user.username,
        # redirect back to the main site
        if self.request.user.username != self.kwargs["username"]:
            return redirect("/")
        fn = otp_required(
            super().dispatch, login_url=self.get_success_url(), redirect_field_name=None
        )
        return fn(*args, **kwargs)

    def form_valid(self, form):
        """This function has been overwritten to make it use get_success_url"""
        for device in devices_for_user(self.request.user):
            device.delete()
        return redirect(self.get_success_url())


class AdminTwoFactorSetup(otp_views.SetupView, SuperAdminOrThisSiteMixin):
    def get_success_url(self):
        return reverse(
            "admin_otp_setup_complete",
            kwargs={"slug": self.kwargs["slug"], "username": self.kwargs["username"]},
        )

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        site = get_object_or_404(Site, uid=self.kwargs["slug"])
        context["site"] = site
        # url to redirect to when the user clicks cancel
        context["cancel_url"] = reverse("users", kwargs={"slug": site.uid})
        return context

    def get(self, request, *args, **kwargs):
        """
        Start the setup wizard. Redirect if already enabled.
        This function has been overwritten in order to redirect
        when the username does not match
        """
        # If the username in the url doesn't match request.user.username,
        # redirect back to the main site
        if self.request.user.username != self.kwargs["username"]:
            return redirect("/")
        elif default_device(self.request.user):
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def done(self, form_list, **kwargs):
        """
        Finish the wizard. Save all forms and redirect.
        This function has been overwritten to make it
        use get_success_url in the final redirect.
        All other lines are unchanged.
        """
        # Remove secret key used for QR code generation
        try:
            del self.request.session[self.session_key_name]
        except KeyError:
            pass

        method = self.get_method()
        # TOTPDeviceForm
        if method.code == "generator":
            form = [form for form in form_list if isinstance(form, TOTPDeviceForm)][0]
            device = form.save()

        # PhoneNumberForm / YubiKeyDeviceForm / EmailForm / WebauthnDeviceValidationForm
        elif method.code in ("call", "sms", "yubikey", "email", "webauthn"):
            device = self.get_device()
            device.save()

        else:
            raise NotImplementedError("Unknown method '%s'" % method.code)

        django_otp.login(self.request, device)
        return redirect(self.get_success_url())


@method_decorator(otp_check, name="dispatch")
class AdminTwoFactorSetupComplete(
    otp_views.SetupCompleteView, SuperAdminOrThisSiteMixin
):
    def get_context_data(self, **kwargs):
        context = {
            "phone_methods": get_available_phone_methods(),
        }
        user = self.request.user
        site = get_object_or_404(Site, uid=self.kwargs["slug"])
        context["site"] = site
        context["user"] = user
        return context

    def dispatch(self, request, *args, **kwargs):
        # Override the dispatch method in order to redirect to site root
        # if the url username does not match request.user.username
        if request.user.username != kwargs["username"]:
            return redirect("/")
        # Everything below this point is unchanged from the
        # standard django View dispatch
        if request.method.lower() in self.http_method_names:
            handler = getattr(
                self, request.method.lower(), self.http_method_not_allowed
            )
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)


@method_decorator(otp_check, name="dispatch")
class AdminTwoFactorBackupTokens(otp_views.BackupTokensView, SuperAdminOrThisSiteMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["site"] = get_object_or_404(Site, uid=self.kwargs["slug"])
        return context

    def dispatch(self, request, *args, **kwargs):
        # Override the dispatch method in order to redirect to site root
        # if the url username does not match request.user.username
        if request.user.username != kwargs["username"]:
            return redirect("/")
        # Everything below this point is unchanged from the
        # standard django View dispatch
        if request.method.lower() in self.http_method_names:
            handler = getattr(
                self, request.method.lower(), self.http_method_not_allowed
            )
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Delete existing backup codes and generate new ones.
        This function has been overwritten in order to change success_url
        """
        device = self.get_device()
        device.token_set.all().delete()
        for n in range(self.number_of_tokens):
            device.token_set.create(token=StaticToken.random_token())

        # Stay on this page after generating new backup tokens
        success_url = reverse("admin_otp_backup", kwargs=self.kwargs)

        return redirect(success_url)
