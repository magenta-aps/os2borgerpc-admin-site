from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView

from django.contrib import admin

from .api import api as user_api
from .client_api import api as client_api

from django_xmlrpc.views import handle_xmlrpc
from markdownx import urls as markdownx
from two_factor.urls import urlpatterns as tf_urls

admin.autodiscover()

urlpatterns = [
    # Login-related
    path("", include("account.urls")),
    # xmlrpc
    path("xmlrpc/", handle_xmlrpc, name="xmlrpc"),
    path("admin-xml/", handle_xmlrpc),
    # Include each of our apps' URLs
    path("", include("system.urls")),
    path("documentation/", include("docs.urls")),
    # Include changelog URLs
    path("changelog/", include("changelog.urls")),
    # Include external apps' URLs
    path("markdownx/", include(markdownx)),
    path("", include(tf_urls)),
    # Admin documentation:
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    # Django admin:
    path("admin/", admin.site.urls),
    # API
    # API effectively has its own urls specified in api.py, besides its builtin docs
    # Redirect /api/ to the docs just for convenience?
    path("api/", RedirectView.as_view(url="/api/docs")),
    path("api/", user_api.urls),
    path("client-api/", client_api.urls),
    # SSO
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("sso/", RedirectView.as_view(url="/oidc/authenticate")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
