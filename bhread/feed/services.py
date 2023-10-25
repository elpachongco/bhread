"""services.py contains functions that save data to the db
Business logic should be in this file.
https://github.com/HackSoftware/Django-Styleguide#selectors
Function naming <entity>_<action>
Use plural entity name if dealing with multiple items.

Service objects are used by calling Service.execute({inputs})
"""

import re
from datetime import timedelta
from typing import Dict, List, Optional
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from service_objects.errors import InvalidInputsError

# from feed import selectors as sel
# from feed import tasks
from service_objects.fields import DictField, ModelField
from service_objects.services import ModelService, Service

from .models import Category, Feed, GroupConfig, Post, User, Vote


def entry_get_categories(entry) -> List[str]:
    """Return a list of strings containing the category tags of
    a feed entry.
    """
    categories = []
    if "tags" not in entry:
        return categories
    for tag in entry.tags:
        if "term" in tag:
            categories.append(tag["term"])
    return categories


def content_to_html(entry_content) -> str:
    """Convert feed entry content to html"""
    c = ""
    for content in entry_content:
        if content["type"] == "text/plain":
            continue
        c += content["value"]
    return c


def feed_update_all():
    """Update all feeds every FEED_SCAN_INTERVAL_MINUTES
    WARNING: Don't rename this function. It's used in `makeschedules`
    command.
    """

    for feed in Feed.objects.filter(
        last_scan__lte=timezone.now()
        - timedelta(minutes=settings.FEED_SCAN_INTERVAL_MINUTES)
    ):
        UpdateFeed.execute({"feed": feed})
    # tasks.feed_update(feed)


def feed_make_verification_string(name):
    return "bhread.com" + reverse("proof", args=[name])


def url_same_origin(url1, url2) -> bool:
    """Compare two urls are from the same site"""
    return urlparse(url1).netloc == urlparse(url2).netloc


def html_clean(s: str):
    soup = BeautifulSoup(s, features="lxml")
    removes = soup(["style", "script", "meta", "link", "head"])
    for r in removes:
        r.decompose()
    return str(soup)


def html_find_reply(s: str, reply_format="replying to") -> Dict[str, Optional[str]]:
    """Find reply string in a string
    Returns the url replying to and the string before the url.
    """
    reply = {"url": None, "reply_string": None}
    soup = BeautifulSoup(s, features="lxml")
    for a_tag in soup.find_all("a"):
        for parent_string in a_tag.parent.strings:
            if reply_format in parent_string:
                reply["url"] = a_tag["href"]  # Get absolute url
                reply["reply_string"] = parent_string
                for s in a_tag.strings:
                    reply["reply_string"] += s
                return reply

    return reply


def html_find_repost_link(html: str, self_url: str) -> Optional[str]:
    """Based on the protocol, this should scan all links
    and see if any of them is in the db.

    Return the first url with a match or None

    Implementation notes:
    This should not detect its own url.
    """
    urls = []

    soup = BeautifulSoup(html, features="lxml")
    for element in soup.find_all("a", href=True):
        href = element["href"]
        if not href.startswith("#"):
            if href == self_url:
                """
                NOTE: This doesn't consider urls that select an id
                e.g. a.com/#Title vs a.com/
                """
                continue
            urls.append(href)

    if not urls:
        return None

    in_db = Post.objects.filter(url__in=urls)
    """This may result in multiple Posts"""

    refer = None
    for url in urls:
        if refer is not None:
            break  # We have found it
        for post in in_db:  # in_db is query set, can optimize here
            if url == post.url:
                refer = url

    return refer


def html_find_group_name(html: str) -> Optional[str]:
    """Returns name of group or none
    NOTE:
    - Add a handler for type of text accepted (should be url compatible).
    - Also, max length.
    - Warning: this allows bhread.com/makegroup/myname</html> as groupname!
    """
    pattern = r"bhread\.com/makegroup/[a-zA-Z0-9/_\-]+"
    register_string = re.search(pattern, html)

    if not register_string:
        return None

    register_string = register_string.group()

    group_name = register_string[len("bhread.com/makegroup/") :]
    return group_name


def html_find_verification_url(html: str) -> str:
    """Returns string of username if verification is found.
    Returns None otherwise.
    """
    search = "bhread.com/feeds/"
    delimiter = "/verification"

    idx = html.find(search)

    if idx == -1:
        return None

    from_search = html[idx:]  # Scan name until the delimiter
    delim_idx = from_search.find(delimiter)
    result = from_search[:delim_idx]
    a = len("bhread.com/feeds/")
    user_name = result[a:]

    return user_name


def post_render(post):
    if post.parent:
        post.content = html_clean(post.content)
    elif post.content:
        post.content = BeautifulSoup(post.content, features="lxml").text[:355]
    return post


class RegisterFeed(Service):
    url = forms.URLField()

    def process(self):
        url = self.cleaned_data["url"]

        feed, created = Feed.objects.get_or_create(url=url)

        if created:
            feed.last_scan = timezone.now()
        # if not created and feed.last_scan -
        # consider interval of scanning.

        parsed = feedparser.parse(url)
        if parsed.bozo:
            raise InvalidInputsError("url", "not a valid feed")
        return created


class CreatePost(Service):
    """Create post. Requires at least the url
    returns a post no matter if it's created or updated.
    If post is existing, it will update.
    """

    feed = ModelField(Feed, required=False)
    url = forms.URLField()
    title = forms.CharField(required=False)
    content = forms.CharField(required=False)

    def process(self):
        feed = self.cleaned_data["feed"]
        url = self.cleaned_data["url"]
        title = self.cleaned_data["title"]
        content = self.cleaned_data["content"]

        post = None
        # if (feed, title, content) == (None, None, None):
        #     post = Post.objects.get_or_create(url=url)
        # else:
        post, created = Post.objects.update_or_create(
            defaults={
                "feed": feed,
                "content": content,
                "title": title,
            },
            url=url,
        )

        if content:
            post = ProcessPost().execute({"post": post})

        return post

    def service_clean(self):
        super().service_clean()
        self.cleaned_data["content"] = html_clean(self.cleaned_data["content"])


class ProcessFeedEntry(Service):
    """
    execute({
        "entry": {dict returned by feedparser.parse().entries[i]},
        "feed": Feed model object
    }
    """

    entry = DictField()
    feed = ModelField(Feed)

    def process(self):
        entry = self.cleaned_data["entry"]
        feed = self.cleaned_data["feed"]

        if not feed.is_verified:
            try:
                VerifyFeed().execute(
                    {
                        "url": entry["link"],
                        "feed": feed,
                    }
                )
            except User.DoesNotExist:
                raise InvalidInputsError(
                    {
                        "entry": "Cannot verify to \
                                          non-existing user"
                    },
                    "",
                )

        post = CreatePost().execute(
            {
                "feed": feed,
                "url": entry["link"],
                "title": entry["title"],
                "content": content_to_html(entry["content"]),
            }
        )

        categories: List[str] = entry_get_categories(entry)

        category_objs = []
        for category in categories:
            try:
                instance, _ = Category.objects.get_or_create(name=category)
            except ValidationError:
                continue
            category_objs.append(instance)

        post.categories.add(*category_objs)
        return post


class ProcessPost(Service):
    """See contents of a post and find its reply, references, group,
    and categories.
    """

    post = ModelField(Post)

    def process(self):
        post = self.cleaned_data["post"]
        content = post.content
        post.feed.owner

        reply = html_find_reply(content)
        repost_link = html_find_repost_link(content, post.url)
        group_name = html_find_group_name(content)

        if reply["url"] is not None:
            post.parent = CreatePost().execute({"url": reply["url"]})
        elif repost_link:
            post.repost = repost_link

        # TODO Check if repost treats group registration link as repost link.
        if group_name:
            group = CreateGroup().execute({"name": group_name})
            post.group_config = group

        post.save()
        return post

    def service_clean(self):
        super().service_clean()
        self.cleaned_data["post"] = self.cleaned_data["post"]


class CreateGroup(ModelService):
    class Meta:
        model = GroupConfig
        fields = "__all__"

    def process(self):
        name = self.cleaned_data["name"]

        group = GroupConfig(name=name)
        group.save()
        return group


class UpdateFeed(Service):
    """Update a feed.
    - If feed is unverified, check feed text for verification string
    - else, create each post.
    - For each post that is a reply, create its parent post
    - If user is verified and post is not a reply, create the post.
    """

    feed = ModelField(Feed)

    def process(self):
        feed = self.cleaned_data["feed"]
        parsed = feedparser.parse(feed.url)  # Add etag and last modified
        if "entries" not in parsed:
            return

        for entry in parsed.entries:
            try:
                ProcessFeedEntry().execute({"entry": entry, "feed": feed})
            except InvalidInputsError:
                continue

        feed.last_scan = timezone.now()
        feed.save()


class VerifyFeed(Service):
    """Verifies feed based on content.
    If success, feed will be owned by `user_name`.
    If no content is provided, fetch the website.
    Will create the post with url

    raises Does not exist error if user that is verifying
    does not exist
    """

    url = forms.URLField()
    feed = ModelField(Feed)
    html_content = forms.CharField(required=False)
    html_title = forms.CharField(required=False)

    def process(self) -> bool:
        feed = self.cleaned_data["feed"]
        url = self.cleaned_data["url"]
        html_content = self.cleaned_data["html_content"]
        html_title = self.cleaned_data["html_title"]
        verified = False

        if not url_same_origin(feed.url, url):
            raise InvalidInputsError(
                {
                    "url": "Verification URL must be from \
                                      same domain as feed."
                },
                "",
            )

        if not html_content:
            try:
                html_content = requests.get(url).text
            except requests.exceptions.RequestException:
                return verified
            html_title = "Verification Post"

        user_name = html_find_verification_url(html_content)
        if user_name:
            user = User.objects.get(username=user_name)

            feed.is_verified = True
            verified = True

            post = CreatePost().execute(
                {
                    "feed": feed,
                    "url": url,
                    "title": html_title,
                    "content": html_content,
                }
            )

            feed.verification = post
            feed.owner = user
            feed.save()

        return verified


class VotePost(Service):
    """Vote a post. Returns True if new vote created"""

    user = ModelField(User)
    post = ModelField(Post)

    def process(self):
        user = self.cleaned_data["user"]
        post = self.cleaned_data["post"]

        vote, created = post.votes_total.get_or_create(voter=user)
        if not created:
            vote.delete()
        return created


class FeedSubscribe:
    """Subscribe to a feed. Returns True if successful."""

    feed = ModelField(Feed)
    user = ModelField(User)

    def process(self) -> bool:
        user = self.cleaned_data["user"]
        feed = self.cleaned_data["feed"]

        user.profile.subscriptions.add(feed)
        return True
