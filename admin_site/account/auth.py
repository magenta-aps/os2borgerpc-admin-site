import jwt
import requests
import logging

from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from django.contrib.auth.models import User

from account.models import UserProfile, SiteMembership, Site
from system.models import Customer

logger = logging.getLogger(__name__)


class MyOIDCAB(OIDCAuthenticationBackend):
    """Override the default OIDCAuthenticationBackend to integrate mozilla_django_oidc with our application"""

    # TODO: Ideally we override get_or_create_user and do error handling in there instead of here, and then this function should return self.UserModel.objects.none() on errors.
    def filter_users_by_claims(self, claims):
        upn = claims.get("upn")
        try:
            user = User.objects.get(username=upn)
            return [user]

        except User.DoesNotExist:
            return self.UserModel.objects.none()

    def create_user(self, claims):
        user = super(MyOIDCAB, self).create_user(claims)
        user.username = claims.get("upn", "")
        user.email = claims.get("email", "")
        user.password = ""
        user.save()

        profile = UserProfile.objects.create(user=user)

        roles = claims.get("roles", "")
        self.configure_sites_access_and_roles(roles, profile)

        return user

    def update_user(self, user, claims):
        user.username = claims.get("upn", "")
        user.email = claims.get("email", "")
        user.password = ""
        user.save()

        profile = UserProfile.objects.get(user=user)

        roles = claims.get("roles", "")
        self.configure_sites_access_and_roles(roles, profile)

        return user

    def get_userinfo(self, access_token, id_token, payload):
        """Return user details dictionary. The id_token and payload are not used in
        the default implementation, but may be used when overriding this method.
        NB: "roles" are extracted from payload and added to user_response."""

        user_response = requests.get(
            self.OIDC_OP_USER_ENDPOINT,
            headers={"Authorization": "Bearer {0}".format(access_token)},
            verify=self.get_settings("OIDC_VERIFY_SSL", True),
            timeout=self.get_settings("OIDC_TIMEOUT", None),
            proxies=self.get_settings("OIDC_PROXY", None),
        )

        user_response.raise_for_status()

        user_response_json = user_response.json()
        user_response_json["roles"] = payload.get("roles")
        user_response_json["upn"] = jwt.decode(
            access_token, options={"verify_signature": False}
        ).get("upn")

        return user_response_json

    def configure_sites_access_and_roles(self, roles, user_profile):
        site_uids = list(
            Customer.objects.get(id=settings.OIDC_CUSTOMER)
            .sites.all()
            .values_list("uid", flat=True)
        )
        # NB! Assumes that a user is only associated with one customer
        SiteMembership.objects.filter(user_profile=user_profile).delete()
        if "all_customeradmin" in roles:
            for site_uid in site_uids:
                SiteMembership.objects.create(
                    user_profile=user_profile,
                    site=Site.objects.get(uid=site_uid),
                    site_user_type=SiteMembership.CUSTOMER_ADMIN,
                )
        else:
            for role in roles:
                try:
                    site_uid, site_role = role.split("_")
                except ValueError:
                    logger.error(
                        f"SSO error: A received role does not contain the delimiter: _. The role was: {role}."
                    )
                    return redirect(reverse("login") + "?sso_error=true")
                if site_uid in site_uids:
                    if site_role.lower() == "siteadmin":
                        site_user_type = SiteMembership.SITE_ADMIN
                    elif site_role.lower() == "siteuser":
                        site_user_type = SiteMembership.SITE_USER
                    else:
                        logger.error(
                            f"SSO error: A received role does not match a role in this application. The role was: {site_role}."
                        )
                        return redirect(reverse("login") + "?sso_error=true")
                    SiteMembership.objects.create(
                        user_profile=user_profile,
                        site=Site.objects.get(uid=site_uid),
                        site_user_type=site_user_type,
                    )

    def verify_claims(self, claims):
        """Verify the provided claims to decide if authentication should be allowed.
        OVERRIDE: Claim validation altered. Also added roles check."""
        if (
            not claims
            or "upn" not in claims
            or "email" not in claims
            or "roles" not in claims
        ):
            logger.error(
                f"SSO error: Received insufficent claims"
            )
            return False
        if (not self.validate_roles(claims)):
            return False
        
        return True

    def validate_roles(self, claims):
        """NOT an override method."""
        roles = claims.get("roles", "")
        user = claims.get("upn")
        site_uid_check = []
        for role in roles:
            try:
                site_uid, site_role = role.split("_")  
                site_uid_check.append(site_uid)      
            except ValueError:
                logger.error(
                    f"SSO error: A received role does not contain the delimiter: _. The role was: {role}."
                )
                return False
            
            if(site_uid in site_uid_check):
                logger.error(
                    f"SSO error: It seems \"{user}\" has more than one role for the site \"{site_uid}\"."
                )
                return False
            
        return True