from system.views import SuperAdminOrThisSiteMixin
from system.models import Site

from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse

import django_otp
from two_factor.forms import TOTPDeviceForm
from two_factor.utils import default_device
from two_factor import views as otp_views
from two_factor.plugins.phonenumber.utils import get_available_phone_methods
from django_otp.decorators import otp_required
from django_otp import devices_for_user, user_has_device
from django_otp.plugins.otp_static.models import StaticToken

from django.forms import Form


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
