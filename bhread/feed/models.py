from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint


class Feed(models.Model):
    class Meta:
        constraints = [
            UniqueConstraint(
                "owner",
                "url",
                name="owner_url_unique",
                violation_error_message="User cannot submit duplicate feeds",
            ),
        ]

    name = models.CharField(max_length=80, default="", blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    verification = models.ForeignKey(
        "Post",
        on_delete=models.SET_NULL,
        null=True,
        related_name="verification_post",
    )
    url = models.URLField(max_length=200)
    etag = models.CharField(max_length=256, null=True)
    last_modified = models.CharField(max_length=256, null=True)
    last_scan = models.DateTimeField(default=datetime.min)
    image = models.URLField(max_length=200, unique=False, default="", blank=True)
    reply_format = models.CharField(max_length=256, default="replying to")

    is_verified = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    is_bozo = models.BooleanField(default=False)

    def __str__(self):
        return f"Feed: {self.url}"

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)


class Post(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, null=True)
    url = models.URLField(
        max_length=200
    )  # must be Unique (don't accept posts from unverified users.
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="parent_post"
    )
    ancestor = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="ancestor_post"
    )
    title = models.CharField(max_length=100, null=True)
    # TODO: Put body content only
    content = models.TextField(null=True)
    # summary = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post {self.pk} - \
            {self.url}\nReplying to {self.parent}"

    class Meta:
        constraints = [UniqueConstraint("feed", "url", name="feed_post_unique")]


class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now=True)
    is_voted = models.BooleanField(default=False)


class Page(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="")
    description = models.TextField(default="")
