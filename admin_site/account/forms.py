from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from account.models import SiteMembership, UserProfile


class UserLinkForm(forms.Form):
    linkable_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=_("Select users to be added to this site"),
        help_text=_("Hold down Ctrl to select multiple users"),
    )

    usertype = forms.ChoiceField(
        required=True,
        choices=SiteMembership.type_choices,
        label=_("Select the usertype that the users should be added with"),
    )

    def setup_usertype_choices(self, loginuser_type, is_superuser):
        self.fields["usertype"].choices = [
            (num, text) for num, text in SiteMembership.type_choices if num <= 2
        ]


class UserForm(forms.ModelForm):
    usertype = forms.ChoiceField(
        required=False,
        choices=SiteMembership.type_choices,
        label=_("Usertype"),
    )

    language = forms.ChoiceField(
        required=True,
        choices=UserProfile.language_choices,
        label=_("Language"),
    )

    new_password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={"class": "passwordinput"}),
        required=False,
    )

    password_confirm = forms.CharField(
        label=_("Password (again)"),
        widget=forms.PasswordInput(attrs={"class": "passwordinput"}),
        required=False,
    )

    class Meta:
        model = User
        exclude = (
            "groups",
            "user_permissions",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "is_superuser",
            "date_joined",
            "last_login",
            "password",
        )

    def __init__(self, *args, **kwargs):
        initial = kwargs.setdefault("initial", {})
        if "instance" in kwargs and kwargs["instance"] is not None:
            user_profile = kwargs["instance"].user_profile
            site = kwargs.pop("site")
            site_membership = user_profile.sitemembership_set.get(site=site)
            initial["usertype"] = site_membership.site_user_type
            initial["language"] = user_profile.language
        else:
            initial["usertype"] = SiteMembership.SITE_USER
            language = kwargs.pop("language", None)
            if language is not None:
                initial["language"] = language
        super().__init__(*args, **kwargs)

    def set_usertype_limited_choices(self, choice_type):
        self.fields["usertype"].choices = [
            (num, text)
            for num, text in SiteMembership.type_choices
            if num <= choice_type
        ]
        if choice_type == SiteMembership.SITE_USER:  # Only one choice
            self.fields["usertype"].disabled = True

    # Sets the choices in the usertype widget depending on the usertype
    # of the user currently filling out the form
    def setup_usertype_choices(self, loginuser_type, is_superuser):
        if is_superuser or loginuser_type == SiteMembership.CUSTOMER_ADMIN:
            # superusers and customer admins can both
            # choose customer admin, site admin or site user.
            self.fields["usertype"].choices = SiteMembership.type_choices
        else:
            # Other users can only choose their own user type
            # or less privileged user types
            # If there is only one choice, set the field to read-only
            self.set_usertype_limited_choices(loginuser_type)

    def clean(self):
        cleaned_data = self.cleaned_data
        pw1 = cleaned_data.get("new_password")
        pw2 = cleaned_data.get("password_confirm")
        if pw1 != pw2:
            raise forms.ValidationError(_("Passwords must be identical."))

        form_username = cleaned_data.get("username")
        user_exists = self.Meta.model.objects.filter(username=form_username).exists()

        if not self.instance.username == form_username and user_exists:
            raise forms.ValidationError(
                _('A user named "%s" already exists.') % form_username
            )
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data["new_password"]:
            user.set_password(self.cleaned_data["new_password"])
        if commit:
            user.save()
        return user


class UserFormSSO(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # The form receives this argument that only the regular UserForm needs
        kwargs.pop("site")

        initial = kwargs.setdefault("initial", {})
        user_profile = kwargs["instance"].user_profile
        initial["language"] = user_profile.language

        super().__init__(*args, **kwargs)

    language = forms.ChoiceField(
        required=True,
        choices=UserProfile.language_choices,
        label=_("Language"),
    )

    class Meta:
        model = User
        fields = ("language",)
