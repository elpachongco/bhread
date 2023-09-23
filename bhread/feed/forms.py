from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from feed import services as ser

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
    # If passed a url belonging to post already existing, this will
    # invalidate the form
    class Meta:
        model = Post
        fields = ["url", "feed"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["feed"].queryset = Feed.objects.filter(owner=self.user)

    def clean(self):
        """Check if Post exists or if Post belongs to Feed site"""
        cleaned_data = super().clean()
        post_url = cleaned_data.get("url")
        feed = cleaned_data.get("feed")

        if Post.objects.filter(url=post_url, feed=feed).exists():
            self.instance = Post.objects.get(url=post_url, feed=feed)

        if not ser.url_same_origin(post_url, feed.url):
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


class SearchForm(forms.Form):
    search = forms.CharField()
