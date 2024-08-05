from django.urls import re_path

from .views import (
    DocView,
)

urlpatterns = [
    re_path(r"^(?P<name>[\d\w\/]+)/", DocView.as_view(), name="doc"),
    re_path(r"^/", DocView.as_view(), name="doc_root"),
]
