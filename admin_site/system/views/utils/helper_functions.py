from system.models import Script, ConfigurationEntry, PC
from django_otp import user_has_device
from django.contrib.auth.decorators import login_required, user_passes_test


def run_wake_plan_script(site, pcs, args, user, type="remove"):
    if type == "set":
        script = Script.objects.get(uid="wake_plan_set")
    else:
        script = Script.objects.get(uid="wake_plan_remove")
    script.run_on(site, pcs, *args, user=user)


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


def site_pcs_stats(context, site_list):
    context["borgerpc_count"] = PC.objects.filter(
        site__in=site_list,
        configuration__entries__key="os2_product",
        configuration__entries__value="os2borgerpc",
    ).count()
    context["borgerpc_kiosk_count"] = PC.objects.filter(
        site__in=site_list,
        configuration__entries__key="os2_product",
        configuration__entries__value="os2borgerpc kiosk",
    ).count()
    # Add counts for each _os_release
    context["releases"] = []
    for release in (
        ConfigurationEntry.objects.filter(key="_os_release")
        .order_by("value")
        .distinct("value")
        .values("value")
    ):
        context["releases"].append(
            (
                release["value"],
                PC.objects.filter(
                    site__in=site_list,
                    configuration__entries__key="_os_release",
                    configuration__entries__value=release["value"],
                ).count(),
            )
        )
    return context
