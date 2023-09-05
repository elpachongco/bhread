from django.test import TestCase
from user.models import User

from .models import Feed, Post
from .services import post_get_ancestors


class PrototypeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("a")

        self.feed = Feed(
            user=self.user,
            url="https://test.com",
            blog_url="https://test.com",
            has_etag=False,
            has_last_modified=False,
        ).save()

        self.posts = []
        self.posts.append(
            Post(
                feed=self.feed,
                url="https://test.com/post",
                is_reply=False,
                content="",
                title="",
            ).save()
        )

    def test_ancestors_from_one_generation(self):
        for post in post_get_ancestors():
            self.assertEqual(post, "")
