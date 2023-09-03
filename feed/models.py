from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


class Feed(models.Model):
    name = models.CharField(max_length=80)
    url = models.URLField(
        max_length=200
    )  # Can't be unique unless decouple feed, normalize urls
    has_etag = models.BooleanField(default=False)  # TODO: Implement
    has_last_modified = models.BooleanField(default=False)
    etag = models.CharField(max_length=256, null=True)
    last_modified = models.CharField(max_length=256, null=True)
    favicon = models.URLField(max_length=200, unique=False, default="", blank=True)
    reply_format = models.CharField(max_length=256, default="replying to")
    is_bozo = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    last_scan = models.DateTimeField(default=datetime.min)

    def __str__(self):
        return f"Feed: {self.url}"

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)


class Post(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, null=True)
    url = models.URLField(max_length=200)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="parent_post"
    )
    ancestor = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="ancestor_post"
    )
    title = models.CharField(max_length=100, default="")
    # TODO: Put body content only
    content = models.TextField(default="")
    # summary = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post {self.pk} - \
            {self.url}\nReplying to {self.parent}"


class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now=True)
    is_voted = models.BooleanField(default=False)


class Page(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="")
    description = models.TextField(default="")
