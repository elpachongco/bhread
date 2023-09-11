from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import Feed, Page, Post


class FeedForm(forms.ModelForm):
    def clean(self):
        """Check if feed is unique for user."""
        # Use the parent's handling of required fields, etc.
        cleaned_data = super().clean()
        if Feed.objects.filter(
            url=cleaned_data.get("url"), owner=self.instance.owner
        ).exists():
            raise ValidationError(
                _("Can't save duplicate feeds."),
                code="invalid",
            )


class FeedRegisterForm(FeedForm):
    class Meta:
        model = Feed
        fields = ["url"]


class VerificationForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["url", "feed"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["feed"].queryset = Feed.objects.filter(owner=self.user)

    def clean(self):
        """Check if Post belongs to Feed site"""
        # Use the parent's handling of required fields, etc.
        cleaned_data = super().clean()
        if (
            urlparse(cleaned_data.get("url")).netloc
            != urlparse(cleaned_data.get("feed").url).netloc
        ):
            raise ValidationError(
                _(
                    "Verification Post must belong to the same domain/subdomain as feed."
                ),
                code="invalid",
            )


class FeedUpdateForm(FeedForm):
    class Meta:
        model = Feed
        fields = ["url", "name", "is_public", "reply_format", "image"]
        labels = {
            "url": "Feed url",
            "name": "Feed name",
            "is_public": "Feed is public",
            "image": "image",
        }


class PageCreateForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ["name", "description"]
