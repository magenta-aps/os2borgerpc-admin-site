from django.urls import path, re_path

from .views import (
    DocView,
)

urlpatterns = [
    # Some of the urls using this pattern require re_path
    # in order to function correctly
    re_path(r"^(?P<name>[\d\w\/]+)/", DocView.as_view(), name="doc"),
    path("", DocView.as_view(), name="doc_root"),
]
