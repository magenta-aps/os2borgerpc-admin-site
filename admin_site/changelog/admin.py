from django.contrib import admin

from changelog.models import (
    Changelog,
    ChangelogComment,
    ChangelogTag,
)


@admin.register(Changelog)
class ChangelogAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "published",
        "created",
        "updated",
    )
    search_fields = ("title",)
    filter_horizontal = ("tags",)


@admin.register(ChangelogTag)
class ChangelogTagAdmin(admin.ModelAdmin):
    pass


@admin.register(ChangelogComment)
class ChangelogCommentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "created",
        "changelog",
        "content",
    )
    readonly_fields = (
        "created",
        "user",
        "parent_comment",
        "changelog",
    )
