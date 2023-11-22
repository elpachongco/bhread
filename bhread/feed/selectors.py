from collections import deque
from datetime import datetime, timedelta
from typing import Dict, Iterator, List, Optional, Set
from urllib.parse import urlparse

import feedparser
import requests
import requests_cache
from bs4 import BeautifulSoup
from django.db.models import Count, F, OuterRef, Q, Subquery
from django.utils import timezone
from feed import services as ser

from .models import Feed, Post, User, Vote

"""selectors.py is a collection of functions that retrieve data.
1. selectors pull data
2. services push data
https://github.com/HackSoftware/Django-Styleguide#selectors
ancestors - Posts that are not replies
descendants - All Posts that are children of a url.
parent - Post that a post is replying to
"""


def ancestors(*, order_by="-date_added", limit=10):
    """Retrieve all ancestors"""
    posts = []
    for post in Post.objects.filter(parent=None).order_by(order_by):
        if post.url not in posts:
            yield post

        posts.append(post.url)


def children(post):
    posts_url = []

    for post in Post.objects.filter(parent__url=post.url):
        if post.url not in posts_url:
            yield post
            posts_url.append(post.url)
    # return Post.objects.filter(parent=post)  # Previous implementation


def descendants(post) -> Iterator[Post]:
    """Find descendants of post. Useful for getting replies of post"""

    # if not post.parent:
    #     if Post.objects.filter(ancestor=post).exists():
    #         return Post.objects.filter(ancestor=post).all()

    stack: List[Post] = []
    stack.append(post)
    first = True

    while stack:
        stack_item = stack.pop()
        for c in children(stack_item):
            stack.append(c)
        if first:
            first = False
            continue
        yield stack_item


def descendants_count(post: Post):
    # TODO: Need more efficient version
    return len([x for x in descendants(post)])


def feeds() -> Iterator[Feed]:
    return Feed.objects.all().iterator()


def favicon(post):
    default = "https://www.svgrepo.com/show/216701/internet.svg"
    if not post.parent:
        f = ser.get_favicon_path(post.url)
        if f:
            return f
        else:
            if post.feed.favicon:
                return post.feed.favicon
            else:
                return default
    if post.feed.favicon:
        return post.feed.favicon
    f = ser.get_favicon_path(url=post.url)
    return f if f else default


def user_feeds(user) -> Iterator[Feed]:
    return Feed.objects.filter(owner=user)


def user_has_verified(user):
    return Feed.objects.filter(owner=user, is_verified=True).exists()


def posts(post_qset):
    """
    title, content, date, author, author_img, reply_count
    returns a query set
    """
    return post_qset.annotate(
        author_name=F("feed__owner__username"),
        author_img=F("feed__owner__profile__image"),
        reply_count=Count("child"),
    )


def home(id=None):
    """Retrieve homepage posts."""

    a = (
        Post.objects.filter(
            content__isnull=False,
            feed__is_verified=True,
        )
        .select_related("parent", "feed__owner", "feed__owner__profile")
        .order_by("-date_added", "-date_modified")
    )
    if id is not None:
        a = a.filter(id__lt=id)
    return posts(a)


def voted_posts(voter):
    return list(
        Vote.objects.filter(voter=voter, post__isnull=False).values_list(
            "post", flat=True
        )
    )


def post_replies(post: Post) -> Dict:
    """Get all replies of post

    Store all replies, as a single-dimension list of dictionaries.
    containining level info. Level information will be used as indentation.
    [
        { "level": 0, "post": <Post object> },
        { "level": 1, "post": <Post object> },
        { "level": 2, "post": <Post object> },
        { "level": 0, "post": <Post object> },
        { "level": 1, "post": <Post object> },
    ]
    This is intended to be used for displaying replies in the templates
    by doing complex logic here, not in the template
    """
    post_stack = [post]
    head_stack = [post]  # Possible branching points
    current_head = []  # Current branching level/point
    while head_stack:
        head = head_stack.pop()
        c = list(children(head))
        if not c:  # The branch will no longer branch
            while post_stack:
                i = post_stack.pop()
                if i != head:  # Find current head in stack
                    continue
                yield {"level": len(current_head), "post": head}
                # If head is found and the item before it is equal to current
                # head, then it's the last child of the current head.
                # The head has now been fully scanned, remove it.
                if post_stack[-1] == current_head[-1]:
                    post_stack.pop()
                    # Delete branching point as it has now been fully scanned.
                    current_head.pop()
                # Proceed to start of main loop and get the next head_stack
                # item which is the sibling of removed current_head item
                break
            continue
        yield {"level": len(current_head), "post": head}
        # If you have a child, you're a branching point
        current_head.append(head)
        for child in c:
            # Track history of items for finding out if item is a branch
            post_stack.append(child)
            # All of the branch child is a possible branching point
            head_stack.append(child)
