from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth import views as auth_views
from account import views as account_views

from .api import api

from django_xmlrpc.views import handle_xmlrpc
from markdownx import urls as markdownx
from two_factor.urls import urlpatterns as tf_urls

admin.autodiscover()

urlpatterns = [
    # Login-related
    path("", include("account.urls")),
    # xmlrpc
    re_path(r"^xmlrpc/$", handle_xmlrpc, name="xmlrpc"),
    re_path(r"^admin-xml/$", handle_xmlrpc),
    # Include each of our apps' URLs
    re_path(r"^", include("system.urls")),
    re_path(r"^documentation/", include("docs.urls")),
    # Include changelog URLs
    re_path(r"^changelog/", include("changelog.urls")),
    # Include external apps' URLs
    re_path("markdownx/", include(markdownx)),
    re_path("", include(tf_urls)),
    # Admin documentation:
    re_path("admin/doc/", include("django.contrib.admindocs.urls")),
    # Django admin:
    re_path(r"^admin/", admin.site.urls),
    # API
    # API effectively has its own urls specified in api.py, besides its builtin docs
    # Redirect /api/ to the docs just for convenience?
    re_path("^api/$", RedirectView.as_view(url="/api/docs")),
    path("api/", api.urls),
    # SSO
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("sso/", RedirectView.as_view(url="/oidc/authenticate")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
