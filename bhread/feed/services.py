from datetime import timedelta
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urlparse

import feedparser
import requests
import requests_cache
from bs4 import BeautifulSoup
from django.utils import timezone
from feed import selectors as sel

from .models import Feed, Post, User, Vote

"""services.py contains functions that save data to the db
Business logic should be in this file.
https://github.com/HackSoftware/Django-Styleguide#selectors
Function naming <entity>_<action>
Use plural entity name if dealing with multiple items.
"""

session = requests_cache.CachedSession()


def ancestors_fill_content():
    for post in Post.objects.filter(title="", content=""):
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


def feed_make_posts(*, feed: Feed) -> Iterator[Post]:
    """Convert feed entries to Posts if entry is a reply.

    Returns Post if Post with url already exists.
    - If url exists but new data is present, return updated post (keep pk).
    - If post with url doesn't exist, return new post.
    - If post is not new and is not an update, ignore
    """
    d = None
    # if False:  ##  Fix
    #     d = feedparser.parse(
    #         feed.url, etag=feed.etag, modified=feed.last_modified
    #     )  # ~~TODO: check caching http headers~~
    # else:
    d = feedparser.parse(feed.url)
    # feed.last_scan = timezone.now()
    # feed.save()

    # changed = False
    # if "etag" in d:
    #     feed.etag = d.etag
    #     changed = True
    # if "modified" in d:
    #     feed.last_modified = d.modified
    #     changed = True
    # if changed:
    #     feed.save()

    for entry in d.entries:
        content = content_to_html(entry.content)
        title = entry.title
        if Post.objects.filter(feed=feed, url=entry.link).exists():
            #### Test Update functionality
            post = Post.objects.get(feed=feed, url=entry.link)
            update = post_update(post=post, title=title, content=content)
            if update:
                yield update

        else:
            yield Post(feed=feed, url=entry.link, title=title, content=content)


def feed_update(feed: Feed):
    for feed_post in feed_make_posts(feed=feed):
        for p in post_make_posts(post=feed_post, feed=feed):
            p.save()
            feed_post.parent = p
            feed_post.save()

    feed.last_scan = timezone.now()
    feed.save()
    ancestors_fill_content()


def feed_update_all():
    """Create posts"""

    """ This builds the tree of posts """

    for feed in Feed.objects.filter(
        last_scan__lte=timezone.now() - timedelta(minutes=1)
    ):
        feed_update(feed)


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
    removes = soup(["style", "script", "meta", "link"])
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
    else:
        post.content = BeautifulSoup(post.content).text[:355]
    return post


def post_make_posts(post: Post, feed: Feed) -> Iterator[Post]:
    """Create posts from post. If post is a reply, and parent post
    doesn't exist, create the post."""
    stack: List[Post] = []
    stack.append(post)

    while stack:
        stack_item = stack.pop()
        reply = html_find_reply(s=stack_item.content)
        if not reply["url"]:
            continue
        p = None
        if not Post.objects.filter(feed=feed, url=reply["url"]).exists():
            p = Post(
                feed=feed,
                url=reply["url"],
            )
        else:
            p = Post.objects.get(feed=feed, url=reply["url"])

        stack.append(p)
        yield p


def post_update(*, post: Post, content, title) -> Optional[Post]:
    changed = False
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
