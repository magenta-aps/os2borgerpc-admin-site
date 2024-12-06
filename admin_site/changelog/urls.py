from django.urls import path

from changelog.views import (
    ChangelogListView,
)

urlpatterns = [
    path(
        "",
        ChangelogListView.as_view(),
        name="changelogs",
    ),
    path(
        "<int:id>/",
        ChangelogListView.as_view(),
        name="changelog",
    ),
]
