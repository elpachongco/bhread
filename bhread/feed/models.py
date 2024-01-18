"""Refer to protocol.md
"""

from datetime import datetime

import pytz
from django.contrib.auth.models import User
from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint


class Feed(models.Model):
    """Test"""

    name = models.CharField(max_length=80, default="", blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    verification = models.ForeignKey(
        "Post",
        on_delete=models.SET_NULL,
        null=True,
        related_name="verification_post",
    )
    url = models.URLField(max_length=200, unique=True)
    etag = models.CharField(max_length=256, null=True)
    last_modified = models.CharField(max_length=256, null=True)
    last_scan = models.DateTimeField(default=(datetime.min.replace(tzinfo=pytz.UTC)))
    image = models.URLField(max_length=200, unique=False, default="", blank=True)
    reply_format = models.CharField(max_length=256, default="replying to")

    is_verified = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    is_bozo = models.BooleanField(default=False)
    categories = models.ManyToManyField("Category")
    language = models.CharField(max_length=50, default="", blank=True)

    def __str__(self):
        return f"Feed: {self.url}"

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)


class Post(models.Model):
    """
    A post must have at least a URL.
    A post without a feed is a parent post that doesn't exist in the database.
    """

    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, null=True)
    url = models.URLField(max_length=200, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="child"
    )
    refer = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refer_post",
    )
    group_config = models.OneToOneField(
        "GroupConfig", null=True, blank=True, on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=100, null=True)
    content = models.TextField(null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField("Category", blank=True)
    votes_total = models.ManyToManyField("Vote", related_name="post", blank=True)
    # Language
    title_language = models.CharField(max_length=50, default="", blank=True)
    content_language = models.CharField(max_length=50, default="", blank=True)

    def __str__(self):
        return f"Post {self.pk} - \
            {self.url}\nReplying to {self.parent}"


class Vote(models.Model):
    # post = models.ForeignKey(Post, on_delete=models.CASCADE)
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    # is_voted = models.BooleanField(default=True)


class GroupConfig(models.Model):
    name = models.CharField(max_length=100, default="")


class Category(models.Model):
    name = models.CharField(max_length=80)

    def __str__(self):
        return f"{self.name}"
