from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from system.models import (
    PC,
    ConfigurationEntry,
    EventRuleServer,
    FileParameter,
    Input,
    PCGroup,
    Script,
    SecurityEvent,
    Site,
    WakeChangeEvent,
    WakeWeekPlan,
)

time_format = forms.TimeInput(
    attrs={"type": "time", "max": "23:59", "class": "form-control"}, format="%H:%M"
)
date_format = forms.DateInput(
    attrs={"type": "date", "class": "form-control"}, format="%Y-%m-%d"
)


class SiteForm(forms.ModelForm):
    citizen_login_api_password = forms.CharField(
        label=_("Password for login API (e.g. Cicero)"),
        widget=forms.PasswordInput(attrs={"class": "passwordinput"}),
        required=False,
        help_text=_(
            "Necessary for customers who wish to authenticate BorgerPC logins through an API (e.g. Cicero)"
        ),
    )
    booking_api_key = forms.CharField(
        label=_("API key for Easy!Appointments"),
        widget=forms.PasswordInput(attrs={"class": "passwordinput"}),
        required=False,
        help_text=_(
            "Necessary for customers who wish to require booking through Easy!Appointments"
        ),
    )
    citizen_login_api_key = forms.CharField(
        label=_("API key for login API (e.g. Quria)"),
        widget=forms.PasswordInput(attrs={"class": "passwordinput"}),
        required=False,
        help_text=_(
            "Necessary for customers who wish to authenticate BorgerPC logins through an API "
            "that requires an API key (e.g. Quria)"
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            self.fields["uid"].disabled = True
            # Add placeholder if a value exists
            for field_name in [
                "booking_api_key",
                "citizen_login_api_key",
                "citizen_login_api_password",
            ]:
                if getattr(instance, field_name, None):
                    self.fields[field_name].widget.attrs["placeholder"] = (
                        (_("Fill out if you want to update the current password"))
                        if field_name == "citizen_login_api_password"
                        else _("Fill out if you want to update the current value")
                    )

    class Meta:
        model = Site
        exclude = [
            "configuration",
            "country",
            "customer",
        ]


class SiteCreateForm(forms.ModelForm):
    class Meta:
        model = Site
        # uid is added manually in the template to allow for an empty value which then gets created as the site-prefix only
        fields = ("name",)


class PCGroupForm(forms.ModelForm):
    # Need to set up this side of the many-to-many relation between groups
    # and PCs manually.
    pcs = forms.ModelMultipleChoiceField(queryset=PC.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        if "instance" in kwargs and kwargs["instance"] is not None:
            initial = kwargs.setdefault("initial", {})
            initial["pcs"] = [pc.pk for pc in kwargs["instance"].pcs.all()]

        super().__init__(*args, **kwargs)

    def clean(self):
        return self.cleaned_data

    def save(self, commit=True):
        instance = super().save(False)

        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            instance.pcs.clear()
            for pc in self.cleaned_data["pcs"]:
                instance.pcs.add(pc)

        self.save_m2m = save_m2m

        # Do we need to save all changes now?
        if commit:
            instance.save()
            self.save_m2m()

        return instance

    class Meta:
        model = PCGroup
        exclude = ["site", "configuration", "wake_week_plan"]


class ScriptForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["tags"].disabled = True

    class Meta:
        model = Script
        exclude = [
            "site",
            "feature_permission",
            "product",
            "is_security_script",
            "is_hidden",
            "uid",
        ]


class ConfigurationEntryForm(forms.ModelForm):
    class Meta:
        model = ConfigurationEntry
        exclude = ["owner_configuration", "read_only"]


# Currently not used by script run or associated scripts, but only the relevant FileArchive views
# to create or update FileParameters
class FileParameterForm(forms.ModelForm):
    class Meta:
        model = FileParameter
        fields = "__all__"


# Only used by script run, not associated scripts
class ParameterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        script = kwargs.pop("script")
        super().__init__(*args, **kwargs)

        # Crispy: Disable labels on crispy fields when using as_crispy_fields as this form currently creates them manually separately
        self.helper = FormHelper()
        self.helper.form_show_labels = False

        for i, inp in enumerate(script.ordered_inputs):
            name = "parameter_%s" % i
            field_data = {
                "label": inp.name,
                "required": True if inp.mandatory else False,
                "initial": inp.default_value,
            }
            if inp.value_type == Input.FILE:
                self.fields[name] = forms.FileField(**field_data)
            elif inp.value_type == Input.DATE:
                field_data["widget"] = forms.DateInput(attrs={"type": "date"})
                self.fields[name] = forms.DateField(**field_data)
            elif inp.value_type == Input.BOOLEAN:
                field_data["initial"] = "True"
                self.fields[name] = forms.BooleanField(
                    **field_data, widget=forms.CheckboxInput()
                )
            elif inp.value_type == Input.INT:
                self.fields[name] = forms.IntegerField(**field_data)
            elif inp.value_type == Input.TIME:
                field_data["widget"] = forms.TimeInput(attrs={"type": "time"})
                self.fields[name] = forms.CharField(**field_data)
            elif inp.value_type == Input.PASSWORD:
                self.fields[name] = forms.CharField(
                    **field_data,
                    widget=forms.PasswordInput(
                        attrs={
                            "readonly": "",
                            "onfocus": "this.removeAttribute('readonly')",
                            "class": "password-input",
                        }
                    ),
                )
            elif inp.value_type == Input.CHOICE:
                CHOICES = [
                    (option.strip(), option.strip())
                    for option in inp.default_value.split(",")
                ]
                self.fields[name] = forms.ChoiceField(**field_data, choices=CHOICES)
            else:
                self.fields[name] = forms.CharField(**field_data)


class PCForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            self.fields["uid"].disabled = True
            self.fields["mac"].disabled = True

    class Meta:
        model = PC
        exclude = ("configuration", "site", "created", "last_seen", "product")
        widgets = {
            "name": forms.widgets.TextInput(
                attrs={"pattern": r"[a-z0-9A-Z][\-a-z0-9A-Z]{1,40}"}
            ),
        }


class SecurityEventForm(forms.ModelForm):
    class Meta:
        model = SecurityEvent
        fields = ("status", "assigned_user", "note")


class EventRuleServerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = EventRuleServer
        fields = "__all__"
        widgets = {
            "monitor_period_start": time_format,
            "monitor_period_end": time_format,
        }


# Used on the Create and Update views
class WakePlanForm(forms.ModelForm):
    # Picklist related
    groups = forms.ModelMultipleChoiceField(
        queryset=PCGroup.objects.all(), required=False
    )
    wake_change_events = forms.ModelMultipleChoiceField(
        queryset=WakeChangeEvent.objects.all(), required=False
    )

    def __init__(self, *args, **kwargs):
        # Setup for the picklists, so we have access to the groups and wake_change_events for the form
        if "instance" in kwargs and kwargs["instance"] is not None:
            initial = kwargs.setdefault("initial", {})
            initial["groups"] = [group.pk for group in kwargs["instance"].groups.all()]
            initial["wake_change_events"] = [
                event.pk for event in kwargs["instance"].wake_change_events.all()
            ]

        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = (
                field.widget.attrs.get("class", "") + " json-input"
            )

    class Meta:
        model = WakeWeekPlan
        exclude = (
            "site",
            "wake_change_events",
        )

        switch_input = forms.CheckboxInput(
            attrs={"class": "form-check-input fs-5", "role": "switch"}
        )

        widgets = {
            "monday_on": time_format,
            "monday_off": time_format,
            "tuesday_on": time_format,
            "tuesday_off": time_format,
            "wednesday_on": time_format,
            "wednesday_off": time_format,
            "thursday_on": time_format,
            "thursday_off": time_format,
            "friday_on": time_format,
            "friday_off": time_format,
            "saturday_on": time_format,
            "saturday_off": time_format,
            "sunday_on": time_format,
            "sunday_off": time_format,
            "sleep_state": forms.Select(attrs={"class": "form-control"}),
            "enabled": switch_input,
        }


# This should be deleteable later on:
class WakeChangeEventForm(forms.ModelForm):
    class Meta:
        model = WakeChangeEvent
        exclude = ("site",)
        widgets = {
            "name": forms.TextInput(attrs={"id": "wake-change-event-name"}),
            "date_start": date_format,
            "time_start": time_format,
            "date_end": date_format,
            "time_end": time_format,
        }
