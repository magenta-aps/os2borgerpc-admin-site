from two_factor import views as otp_views


class LoginView(otp_views.LoginView):
    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)

        if self.request.resolver_match.url_name == "sso-login-error":
            context["sso_login_error"] = True

        return context
