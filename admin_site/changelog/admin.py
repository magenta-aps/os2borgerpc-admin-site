from django.contrib import admin

import changelog.models as m


@admin.register(m.Changelog)
class ChangelogAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "published",
        "created",
        "updated",
    )
    search_fields = ("title",)
    filter_horizontal = ("tags",)


@admin.register(m.ChangelogTag)
class ChangelogTagAdmin(admin.ModelAdmin):
    pass


@admin.register(m.ChangelogComment)
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
