from two_factor import views as otp_views


class LoginView(otp_views.LoginView):
    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)

        if "sso_error" in self.request.GET:
            context["sso_error"] = True

        return context
