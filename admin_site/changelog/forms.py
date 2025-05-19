# TODO: This might actually be deleteable, because views_dir doesn't use it it seems?!
from django import forms

from changelog.models import (
    ChangelogComment,
)


class ChangelogCommentForm(forms.ModelForm):
    class Meta:
        model = ChangelogComment
        fields = ["content"]
