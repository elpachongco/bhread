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
        # self.assertEqual(1, 2)
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
        self.assertEqual(self.feed.is_verified, False)

        items += [
            make_item(
                title="test item 6",
                link="https://bhread.com/post/6",
                content=f"https://bhread.com/feeds/{self.user.username}/verification",
            ),
        ]
        ser.feed_update(feed=self.feed, parser=customcustomParser)
        self.assertEqual(self.feed.is_verified, True)

    def test_verification_post_is_created(self):
        self.feed.is_verified = False
        self.feed.verification = None
        self.feed.save()
        self.assertEqual(self.feed.is_verified, False)

        items = [
            make_item(
                title="test item 1",
                link="https://bhread.com/post/1",
                content=f"https://bhread.com/feeds/{self.user.username}/verification",
            ),
        ]

        def customcustomParser(url):
            return self.customParser(items)

        ser.feed_update(feed=self.feed, parser=customcustomParser)

        self.assertEqual(self.feed.is_verified, True)
        self.assertEqual(len(Post.objects.all()), 1)
        self.assertEqual(len(Post.objects.filter(url="https://bhread.com/post/1")), 1)

    def test_verify_from_post_owned_by_users_other_feed_does_not_create_new_post(self):
        self.feed.is_verified = False
        self.feed.verification = None
        self.feed.save()

        items = [
            make_item(
                title="test item 1",
                link="https://bhread.com/post/1",
                content=f"https://bhread.com/feeds/{self.user.username}/verification",
            ),
        ]

        def customcustomParser(url):
            return self.customParser(items)

        ser.feed_update(feed=self.feed, parser=customcustomParser)

        self.assertEqual(self.feed.is_verified, True)
        self.assertEqual(len(Post.objects.all()), 1)
        self.assertEqual(len(Post.objects.filter(url="https://bhread.com/post/1")), 1)

        feed_to_verify = Feed.objects.create(
            url="https://bhread.com/other",
            owner=self.user,
        )

        ser.feed_verify_url(feed_to_verify, "https://bhread.com/post/1")
        self.assertEqual(feed_to_verify.is_verified, True)
        self.assertEqual(len(Post.objects.filter(url="https://bhread.com/post/1")), 1)

    def test_verification_from_url(self):
        pass
