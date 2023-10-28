from unittest import mock
from unittest.mock import Mock, PropertyMock, patch

import feedparser
import requests
from django.test import TestCase
from feed import selectors as sel
from feed import services as ser
from feed.models import Category, Feed, GroupConfig, Post
from user.models import User

from .feedgen import make_feed, make_item

# from django.contrib.syndication.views import Feed


class PrototypeTest(TestCase):
    def customParser(self, items):
        """Useful for injecting a parser dependency so that
        no http request will happen.
        """
        return feedparser.parse(
            make_feed(items, link="https://bhread.com/feed/shorts.xml")
        )

    def setUp(self):
        self.user = User.objects.create_user(username="test_user_1", password="bruh")

        self.feed = Feed.objects.create(
            name="testfeed1",
            url="https://bhread.com/feed/shorts.xml",
        )

    def test_playground(self):
        """quick Test code here"""
        pass

    @patch("feed.services.feedparser.http.get")
    def test_scan_of_new_feed(self, mock_get):
        """Test if a newly added valid feed is scanned"""
        items = [
            make_item(
                title="test item 1",
                link="https://bhread.com/post/1",
                content="<html><i>bhread.com/makegroup/crochet</i></html>",
            )
        ]
        new_feed = bytes(make_feed(items, link=self.feed.url), "utf-8")
        mock_get.return_value = new_feed

        ser.UpdateFeed().execute({"feed": self.feed})
        self.assertEqual(len(Post.objects.all()), 1)

    def test_find_repost_link(self):
        Post.objects.create(url="https://bhread.com")
        a = ser.html_find_repost_link(
            """
            <html>
            <a href="https://bhread.com"></a>
            <a href="https://google.com"></a>
            </html>
            """,
            self_url="https://google.com",
        )
        self.assertEqual(a, "https://bhread.com")

    def test_find_group_name(self):
        """Should find group name"""
        a = ser.html_find_group_name(
            """
            <html>
                bhread.com/makegroup/crochet
            </html>
            """
        )
        self.assertEqual(a, "crochet")

        a = ser.html_find_group_name("""<html>bhread.com/makegroup/crochet</html>""")
        self.assertEqual(a, "crochet")

        a = ser.html_find_group_name(
            """<html>bhread.com/makegroup/crochet bhread.com/makegroup/crochet
            </html>
            """
        )
        self.assertEqual(a, "crochet")

        a = ser.html_find_group_name(
            """bhread.com/makegroup/crochet/fun#
            """
        )
        self.assertEqual(a, "crochet/fun")

    @patch("feed.services.feedparser.http.get")
    def test_new_group(self, mock_get):
        """Group must be created when a post creates one"""
        items = [
            make_item(
                title="test item 1",
                link="https://bhread.com/post/1",
                content="<html>bhread.com/makegroup/crochet</html>",
            )
        ]
        new_feed = bytes(make_feed(items, link=self.feed.url), "utf-8")
        mock_get.return_value = new_feed

        # mock_parser.return_value = feedparser.parse(text)
        ser.UpdateFeed().execute({"feed": self.feed})
        self.assertEqual(bool(Post.objects.all()[0].group_config), True)

    @patch("feed.services.feedparser.http.get")
    def test_verification_from_new_feed_post(self, mock_get):
        """If a feed publishes a post with the verification string, it should
        be detected and verified"""

        # Simulate feed publishing posts
        items = [
            make_item(
                title="test item 1",
                link="https://bhread.com/post/1",
                content="<html>test content hello </html>",
            ),
            make_item(
                title="test item 6",
                link="https://bhread.com/post/6",
                content=f"<html><i>https://bhread.com/feeds/{self.user.username}/verification</i></html>",
            ),
        ]

        new_feed = bytes(make_feed(items, link=self.feed.url), "utf-8")
        mock_get.return_value = new_feed

        ser.UpdateFeed().execute({"feed": self.feed})
        self.assertEqual(
            self.feed.is_verified, True, msg="Can't verify from verification post"
        )

    @patch("feed.services.feedparser.http.get")
    def test_reply(self, mock_get):
        """If a post containing the reply string is published, it must be
        recognized as a reply
        """
        # Create a reply to the previous post.
        items = [
            make_item(
                title="test item 1",
                link="https://bhread.com/post/1",
                content="<html>test content hello </html>",
            ),
            make_item(
                title="test item 2",
                link="https://bhread.com/post/2",
                content="<html>replying to <a href='https://bhread.com/post/1'>my previous post</a></html>",
            ),
            make_item(
                title="test item 3",
                link="https://bhread.com/post/3",
                content="<html>replying to <a href='https://bhread.com/post/2'>my previous post</a></html>",
            ),
        ]
        new_feed = bytes(make_feed(items, link=self.feed.url), "utf-8")

        # Override feedparser.parse so it won't do http request
        mock_get.return_value = new_feed
        ser.UpdateFeed().execute({"feed": self.feed})

        # Both replies should be  recognized
        reply = Post.objects.get(url="https://bhread.com/post/2")
        self.assertEqual(reply.parent.url, "https://bhread.com/post/1")
        reply = Post.objects.get(url="https://bhread.com/post/3")
        self.assertEqual(reply.parent.url, "https://bhread.com/post/2")

    @patch("feed.services.feedparser.http.get")
    def test_reply_count(self, mock_get):
        """A post with multiple children of varying depth in the tree must
        return the reply count
        """
        items = [
            make_item(
                title="test item 1",
                link="https://bhread.com/post/1",
                content="<html>test content hello </html>",
            ),
            make_item(
                title="test item 2",
                link="https://bhread.com/post/2",
                content="<html>replying to <a href='https://bhread.com/post/1'>my previous post</a></html>",
            ),
            make_item(
                title="test item 3",
                link="https://bhread.com/post/3",
                content="<html>replying to <a href='https://bhread.com/post/2'>my previous post</a></html>",
            ),
        ]
        new_feed = bytes(make_feed(items, link=self.feed.url), "utf-8")

        # Override feedparser.parse so it won't do http request
        mock_get.return_value = new_feed
        ser.UpdateFeed().execute({"feed": self.feed})

        reply = Post.objects.filter(url="https://bhread.com/post/1")
        reply = sel.posts(reply)
        self.assertEqual(reply[0].reply_count, 2)
