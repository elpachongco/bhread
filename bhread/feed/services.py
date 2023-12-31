from datetime import timedelta
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urlparse

import feedparser
import requests
import requests_cache
from bs4 import BeautifulSoup
from django.urls import reverse
from django.utils import timezone
from feed import selectors as sel
from feed import tasks

from .models import Feed, Post, User, Vote

"""services.py contains functions that save data to the db
Business logic should be in this file.
https://github.com/HackSoftware/Django-Styleguide#selectors
Function naming <entity>_<action>
Use plural entity name if dealing with multiple items.
"""

session = requests_cache.CachedSession()


def ancestors_fill_content():
    for post in Post.objects.filter(title=None, content=None):
        a = requests.get(post.url)
        soup = BeautifulSoup(a.text)
        title = " ".join(soup.title.stripped_strings)
        content = a.text
        post.content = content
        post.title = title
        post.save()


def content_to_html(entry_content):
    c = ""
    for content in entry_content:
        if content["type"] == "text/plain":
            continue
        c += content["value"]
    return c


def feed_get(feed) -> str:
    """Return content of feed as string"""
    # NOTE: THIS SHOULD USE the HTTP 304 status code,
    # NOTE: last_modified, etag
    # a = requests.get(feed.url)
    # return a.text
    # return feedparser.parse()


def feed_make_posts(*, feed: Feed, parsed_feed) -> Iterator[Post]:
    """Convert feed entries to Posts.

    Returns Post if Post with url already exists.
    - If url exists but new data is present, return updated post (keep pk).
    - If post with url doesn't exist, return new post.
    - If post is not new and is not an update, ignore
    """
    if "entries" not in parsed_feed:
        return

    for entry in parsed_feed.entries:
        content = content_to_html(entry.content) if "content" in entry else None
        content = html_clean(content) if content else None
        title = entry.title if "title" in entry else None
        if Post.objects.filter(url=entry.link, feed=feed).exists():
            post = Post.objects.get(url=entry.link, feed=feed)
            update = post_update(post=post, title=title, content=content, feed=feed)
            if update:
                yield update
        else:
            yield Post(feed=feed, url=entry.link, title=title, content=content)


def feed_update(feed: Feed, parser=feedparser.parse):
    """Update a feed.
    - If feed is unverified, check feed text for verification string
    - else, create each post.
    - For each post that is a reply, create its parent post
    - If user is verified and post is not a reply, create the post.
    """
    verified = feed.is_verified
    just_verified = False

    parsed_feed = parser(feed.url)
    for feed_post in feed_make_posts(feed=feed, parsed_feed=parsed_feed):
        if not verified:
            verified = feed_verify(feed, feed_post.content)
            if verified:
                just_verified = True
                feed_post.save()
                feed.verification = feed_post
        else:
            parent = post_make_parent(feed_post)
            if parent is not None:
                parent.save()
                feed_post.parent = parent
            feed_post.save()

    if just_verified and feed.verification:  # Verification should be the latest post.
        feed.verification.date_added = timezone.now()
        feed.verification.save()

    feed.last_scan = timezone.now()
    feed.save()


def feed_update_all():
    """Create posts"""

    for feed in Feed.objects.filter(
        last_scan__lte=timezone.now() - timedelta(minutes=1)
    ):
        tasks.feed_update(feed)


def feed_verify(feed, text_content: str) -> bool:
    """Verify feed.
    If feed.verification post exists, use that.
    Else, fetch feed text and find search string.
    """
    verified = False
    search = feed_make_verification_string(feed.owner.username)
    content = ""
    verification_post = feed.verification

    if verification_post:  # Always use verification post if available
        content = verification_post.content

    if not content:
        content = text_content

    if search in content or search.removesuffix("/") in content:
        if verification_post:
            feed.verification.save()
        verified = True
        feed.is_verified = True
        feed.save()

    return verified


def feed_make_verification_string(name):
    return "bhread.com" + reverse("proof", args=[name])


def feed_verify_url(feed, url) -> bool:
    """Verify feed using a url
    - If feed is already verified, return
    - If url exists in one of user's feeds, use that
    """
    if feed.is_verified:
        return

    if Post.objects.filter(url=url, feed__owner=feed.owner).exists():
        post = Post.objects.get(url=url, feed__owner=feed.owner)
    else:
        post = Post(url=url, feed=feed)

    a = ""
    if post.content:
        a = post.content
    else:
        a = requests.get(url).text
        post.content = html_clean(a)
    feed.verification = post
    verified = feed_verify(feed, a)
    if verified:
        feed_update(feed)
    return verified


def url_same_origin(url1, url2) -> bool:
    """Compare two urls if they're from the same site"""
    return urlparse(url1).netloc == urlparse(url2).netloc


def get_favicon_path(url: str) -> str:
    """Retrieves site favicon of a given url"""
    o = urlparse(url)
    o = o._replace(scheme="https")
    link = o.scheme + "://" + o.netloc

    try:
        page = session.get(link)
    except requests.ConnectionError:
        return ""

    soup = BeautifulSoup(page.text, "html.parser")
    icon_link: Any = soup.find("link", rel="shortcut icon")
    if icon_link is not None:
        icon_link = icon_link.extract()
        icon_link = icon_link["href"]
    else:
        return ""

    if icon_link is None:
        icon_link = soup.find("link", rel="icon")["href"]
    if icon_link is None:
        icon_link = link + "/favicon.ico"
    else:
        a = urlparse(icon_link)
        if a.netloc == "":
            a = a._replace(netloc=o.netloc)
        if a.scheme == "":
            a = a._replace(scheme=o.scheme)
        icon_link = a.geturl()

    return icon_link


def html_clean(s: str):
    soup = BeautifulSoup(s)
    removes = soup(["style", "script", "meta", "link", "head"])
    for r in removes:
        r.decompose()
    return str(soup)


def html_find_reply(s: str, reply_format="replying to") -> Dict[str, str]:
    reply = {"url": "", "reply_string": ""}
    soup = BeautifulSoup(s, features="html.parser")
    for a_tag in soup.find_all("a"):
        for parent_string in a_tag.parent.strings:
            if reply_format in parent_string:
                reply["url"] = a_tag["href"]  # Get absolute url
                reply["reply_string"] = parent_string
                for s in a_tag.strings:
                    reply["reply_string"] += s
                return reply

    return reply


def post_render(post):
    if post.parent:
        post.content = html_clean(post.content)
    elif post.content:
        post.content = BeautifulSoup(post.content).text[:355]
    return post


def post_make_parent(post: Post) -> Optional[Post]:
    """Scan post if it's a reply.
    - If it's a reply
        - Retrieve verified parent if it exists
        - else
    """
    reply = html_find_reply(s=post.content)
    parent_url = reply["url"]
    if parent_url:
        if Post.objects.filter(url=parent_url).exists():
            return Post.objects.get(url=parent_url)
        else:
            return Post(url=parent_url)
    return None


def post_make_parents(post: Post, feed: Feed) -> Iterator[Post]:
    """Create parents from reply posts. If post is a reply, and parent post
    doesn't exist, create the post. If post is not a reply, ignore"""
    stack: List[Post] = []
    urls: List[str] = []  # track unsaved urls
    stack.append(post)
    urls.append(post.url)

    while stack:
        stack_item = stack.pop()
        if not stack_item.content:  # None or empty string
            continue
        reply = html_find_reply(s=stack_item.content)

        if not reply["url"]:
            continue

        parent = None
        if (
            not Post.objects.filter(url=reply["url"]).exists()
            and reply["url"] not in urls
        ):
            parent = Post(
                url=reply["url"],
            )
        else:
            parent = Post.objects.get(url=reply["url"])

        urls.append(parent.url)
        stack.append(parent)
        yield parent


def post_update(*, post: Post, content, title, feed) -> Optional[Post]:
    changed = False
    if post.feed is None and feed is not None:
        post.feed = feed
        changed = True
    if post.content != content:
        post.content = content
        changed = True
    if post.title != title:
        post.title = title
        changed = True
    return post if changed else None


def vote(*, post: Post, user: User) -> Vote:
    if not Vote.objects.filter(post=post, user=user).exists():
        return Vote(post=post, user=user, is_voted=True).save()
    v = Vote.objects.get(post=post, user=user)

    if not v.is_voted:
        v.is_voted = True
        v.save()  # NOTE: Where should save be handled?
        # handle save in the view to save db transaction?
        # tradeoff: more if else, save() to write

    return v


def vote_revert(*, post: Post, user: User) -> Vote:
    if not Vote.objects.filter(post=post, user=user).exists():
        raise Exception("Can't unvote a non-existent vote")
    v = Vote.objects.get(post=post, user=user)

    if v.is_voted:
        v.is_voted = False
        v.save()

    return v
