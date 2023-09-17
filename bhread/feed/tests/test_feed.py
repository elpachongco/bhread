import feedparser
from django.test import TestCase
from feed import selectors as sel
from feed import services as ser
from feed.models import Feed, Post
from user.models import User

from .feedgen import make_feed, make_item

# from django.contrib.syndication.views import Feed


class PrototypeTest(TestCase):
    def customParser(self, items):
        return feedparser.parse(
            make_feed(items, link="https://bhread.com/feed/shorts.xml")
        )

    def setUp(self):
        self.user = User.objects.create_user(username="test_user_1", password="bruh")

        self.feed = Feed.objects.create(
            name="testfeed1",
            owner=self.user,
            url="https://bhread.com/feed/shorts.xml",
            is_verified=True,
        )

    def test_playground(self):
        """quick Test code here"""
        afe = Feed.objects.create(
            owner=self.user,
            url="https://elpachongco.github.io/feed/shorts.xml",
            is_verified=True,
        )
        ser.feed_update(afe)
        self.assertEqual(1, 2)
        pass

    def test_verification_post_is_updated(self):
        """Test if the verification post is duplicated or update"""
        self.feed.is_verified = False
        self.feed.save()
        items = [
            make_item(
                title="1",
                link="https://bhread.com/post/1",
                content=f"bhread.com/feeds/{self.feed.owner.username}/verification",
            ),
        ]

        def customcustomParser(url):
            return self.customParser(items)

        ser.feed_update(self.feed, customcustomParser)

        items = [
            make_item(
                title="1",
                link="https://bhread.com/post/1",
                content=f"Hi there! bhread.com/feeds/{self.feed.owner.username}/verification",
            ),
        ]

        def customcustomParser(url):
            return self.customParser(items)

        ser.feed_update(self.feed, customcustomParser)

        self.assertEqual(
            Post.objects.filter(url="https://bhread.com/post/1").exists(), True
        )
        self.assertEqual(len(Post.objects.filter(feed=self.feed)), 1)

    def test_non_reply_post_recognized_as_post(self):
        items = [
            make_item(title="test item 1", link="https://bhread.com/post/1"),
            make_item(title="test item 2", link="https://bhread.com/post/2"),
            make_item(title="test item 3", link="https://bhread.com/post/3"),
            make_item(title="test item 4", link="https://bhread.com/post/4"),
            make_item(title="test item 5", link="https://bhread.com/post/5"),
        ]

        def customcustomParser(url):
            return self.customParser(items)

        ser.feed_update(feed=self.feed, parser=customcustomParser)
        a = Post.objects.filter(feed=self.feed)
        self.assertEqual(len(a), 5)

    def test_verification_from_new_feed_post(self):
        self.feed.is_verified = False
        self.feed.verification = None
        self.feed.save()

    def test_verification_from_post_url(self):
        pass

    def test_verification_from_site_url(self):
        pass


# TEST FOR relative link resolution ()
