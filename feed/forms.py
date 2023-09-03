from django import forms

from .models import Feed, Page


class FeedRegisterForm(forms.ModelForm):
    class Meta:
        model = Feed
        fields = ["url", "is_public", "reply_format", "favicon"]


class FeedUpdateForm(forms.ModelForm):
    class Meta:
        model = Feed
        fields = ["url", "name", "is_public", "reply_format", "favicon"]
        labels = {
            "url": "Feed url",
            "name": "Feed name",
            "is_public": "Feed is public",
            "favicon": "Favicon url",
        }


class PageCreateForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ["name", "description"]
