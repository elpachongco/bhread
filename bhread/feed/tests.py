import feedparser
from django.test import TestCase
from feed import selectors as sel
from feed import services as ser
from user.models import User

from .models import Feed, Post

# from django.contrib.syndication.views import Feed


ITEM_DATA = """
<entry>
<title type="html">A serious post</title>
<link href="http://localhost:4000/shorts/2023-09-16.html" rel="alternate" type="text/html" title="A serious post" />
<published>2023-09-08T00:40:09+08:00</published>
<updated>2023-09-08T00:40:09+08:00</updated>
<id>http://localhost:4000/shorts/2023-09-16</id>
<content type="html" xml:base="http://localhost:4000/shorts/2023-09-16.html">
Hi! lkjlkjldsafl
</content>
<author>
<name></name>
</author>
<summary type="html">replying to lksjafdHi there!!! It’s a new plfjldsfatform for bloggers.</summary>
</entry>
"""

ITEMS_DATA = """
<entry>
<title type="html">A serious post</title>
<link href="http://localhost:4000/shorts/2023-09-15.html" rel="alternate" type="text/html" title="A serious post" />
<published>2023-09-08T00:40:09+08:00</published>
<updated>2023-09-08T00:40:09+08:00</updated>
<id>http://localhost:4000/shorts/2023-09-15</id>
<content type="html" xml:base="http://localhost:4000/shorts/2023-09-15.html">&lt;p&gt;This is a post introducing bhread.&lt;/p&gt;
&lt;p&gt;It’s a new platform for bloggers.&lt;/p&gt;</content>
<author>
<name></name>
</author>
<summary type="html">This is a post introducing bhread.</summary>
</entry>
<entry>
<title type="html">A serious post</title>
<link href="http://localhost:4000/shorts/2023-09-14.html" rel="alternate" type="text/html" title="A serious post" />
<published>2023-09-08T00:40:09+08:00</published>
<updated>2023-09-08T00:40:09+08:00</updated>
<id>http://localhost:4000/shorts/2023-09-14</id>
<content type="html" xml:base="http://localhost:4000/shorts/2023-09-14.html">&lt;p&gt;This is a post introducing bhread.&lt;/p&gt;

&lt;p&gt;It’s a new platform for bloggers.&lt;/p&gt;</content>
<author>
<name></name>
</author>
<summary type="html">This is a post introducing bhread.</summary>
</entry>
<entry>
<title type="html">Third level Reply to reply also this is a long title</title>
<link href="http://localhost:4000/shorts/2023-09-13.html" rel="alternate" type="text/html" title="Third level Reply to reply also this is a long title" />
<published>2023-08-08T00:40:09+08:00</published>
<updated>2023-08-08T00:40:09+08:00</updated>
<id>http://localhost:4000/shorts/2023-09-13</id>
<content type="html" xml:base="http://localhost:4000/shorts/2023-09-13.html">&lt;p&gt;…replying to &lt;a href=&quot;http://instructables.com&quot;&gt;third reply&lt;/a&gt;&lt;/p&gt;

&lt;p&gt;This is a post about instructables.com&lt;/p&gt;

&lt;h2 id=&quot;testing-header-2&quot;&gt;Testing header 2&lt;/h2&gt;

&lt;p&gt;bhread.com/feeds/admin/verification&lt;/p&gt;</content>
<author>
<name></name>
</author>
<summary type="html">…replying to third reply</summary>
</entry>
<entry>
<title type="html">Third level Reply to reply also this is a long title</title>
<link href="http://localhost:4000/shorts/2023-09-12.html" rel="alternate" type="text/html" title="Third level Reply to reply also this is a long title" />
<published>2023-08-08T00:40:09+08:00</published>
<updated>2023-08-08T00:40:09+08:00</updated>
<id>http://localhost:4000/shorts/2023-09-12</id>
<content type="html" xml:base="http://localhost:4000/shorts/2023-09-12.html">&lt;p&gt;…replying to &lt;a href=&quot;http://instructables.com&quot;&gt;third reply&lt;/a&gt;&lt;/p&gt;

&lt;p&gt;This is a post about instructables.com&lt;/p&gt;

&lt;h2 id=&quot;testing-header-2&quot;&gt;Testing header 2&lt;/h2&gt;

&lt;p&gt;bhread.com/users/admin/verification&lt;/p&gt;</content>
<author>
<name></name>
</author>
<summary type="html">…replying to third reply</summary>
</entry>
<entry>
<title type="html">Third level Reply to reply also this is a long title</title>
<link href="http://localhost:4000/shorts/2023-09-11.html" rel="alternate" type="text/html" title="Third level Reply to reply also this is a long title" />
<published>2023-08-08T00:40:09+08:00</published>
<updated>2023-08-08T00:40:09+08:00</updated>
<id>http://localhost:4000/shorts/2023-09-11</id>
<content type="html" xml:base="http://localhost:4000/shorts/2023-09-11.html">&lt;p&gt;…replying to &lt;a href=&quot;http://instructables.com&quot;&gt;third reply&lt;/a&gt;&lt;/p&gt;

&lt;p&gt;This is a post about instructables.com&lt;/p&gt;

&lt;h2 id=&quot;testing-header-2&quot;&gt;Testing header 2&lt;/h2&gt;

&lt;p&gt;bhread.com/users/admin/verification&lt;/p&gt;</content>
<author>
<name></name>
</author>
<summary type="html">…replying to third reply</summary>
</entry>
<entry>
<title type="html">Third level Reply to reply also this is a long title</title>
<link href="http://localhost:4000/shorts/2023-08-24.html" rel="alternate" type="text/html" title="Third level Reply to reply also this is a long title" />
<published>2023-08-08T00:40:09+08:00</published>
<updated>2023-08-08T00:40:09+08:00</updated>
<id>http://localhost:4000/shorts/2023-08-24</id>
<content type="html" xml:base="http://localhost:4000/shorts/2023-08-24.html">&lt;p&gt;…replying to &lt;a href=&quot;http://instructables.com&quot;&gt;third reply&lt;/a&gt;&lt;/p&gt;

&lt;p&gt;This is a post about instructables.com&lt;/p&gt;

&lt;h2 id=&quot;testing-header-2&quot;&gt;Testing header 2&lt;/h2&gt;</content>
<author>
<name></name>
</author>
<summary type="html">…replying to third reply</summary>
</entry>
<entry>
<title type="html">Third level Reply to reply also this is a long title</title>
<link href="http://localhost:4000/shorts/2023-08-23.html" rel="alternate" type="text/html" title="Third level Reply to reply also this is a long title" />
<published>2023-08-08T00:40:09+08:00</published>
<updated>2023-08-08T00:40:09+08:00</updated>
<id>http://localhost:4000/shorts/2023-08-23</id>
<content type="html" xml:base="http://localhost:4000/shorts/2023-08-23.html">&lt;p&gt;…replying to &lt;a href=&quot;http://localhost:4000/shorts/2023-08-18-test.html&quot;&gt;third reply&lt;/a&gt;&lt;/p&gt;

&lt;p&gt;This is a post about facebook.com&lt;/p&gt;

&lt;h2 id=&quot;testing-header-2&quot;&gt;Testing header 2&lt;/h2&gt;</content>
<author>
<name></name>
</author>
<summary type="html">…replying to third reply</summary>
</entry>
<entry>
<title type="html">Animated Favicons Are Great</title>
<link href="http://localhost:4000/shorts/2023-08-22.html" rel="alternate" type="text/html" title="Animated Favicons Are Great" />
<published>2023-08-08T00:40:09+08:00</published>
<updated>2023-08-08T00:40:09+08:00</updated>
<id>http://localhost:4000/shorts/2023-08-22</id>
<content type="html" xml:base="http://localhost:4000/shorts/2023-08-22.html">&lt;p&gt;…replying to &lt;a href=&quot;http://localhost:4000/shorts/2023-08-13-test.html&quot;&gt;animated favicons&lt;/a&gt;&lt;/p&gt;

&lt;p&gt;aslfdkj&lt;/p&gt;

&lt;p&gt;This is a post about facebook.com&lt;/p&gt;

&lt;h1 id=&quot;lakje&quot;&gt;lakje&lt;/h1&gt;</content>
<author>
<name></name>
</author>
<summary type="html">…replying to animated favicons</summary>
</entry>
<entry>
<title type="html">Reply to reply</title>
<link href="http://localhost:4000/shorts/2023-08-21.html" rel="alternate" type="text/html" title="Reply to reply" />
<published>2023-08-08T00:40:09+08:00</published>
<updated>2023-08-08T00:40:09+08:00</updated>
<id>http://localhost:4000/shorts/2023-08-21</id>
<content type="html" xml:base="http://localhost:4000/shorts/2023-08-21.html">&lt;p&gt;…replying to &lt;a href=&quot;https://facebook.com&quot;&gt;facebook.com&lt;/a&gt;&lt;/p&gt;

&lt;p&gt;This is a post about facebook.com&lt;/p&gt;

&lt;h2 id=&quot;testing-header-2&quot;&gt;Testing header 2&lt;/h2&gt;</content>
<author>
<name></name>
</author>
<summary type="html">…replying to facebook.com</summary>
</entry>

"""

FEED_DATA_START = """
<?xml version="1.0" encoding="utf-8"?>
<feed
xmlns="http://www.w3.org/2005/Atom" >
<generator uri="https://jekyllrb.com/" version="3.8.6">Jekyll</generator>
<link href="http://localhost:4000/feed/shorts.xml" rel="self" type="application/atom+xml" />
<link href="http://localhost:4000/" rel="alternate" type="text/html" />
<updated>2023-09-13T18:16:34+08:00</updated>
<id>http://localhost:4000/feed/shorts.xml</id>
<title type="html">elpachongco’s blog | Shorts</title>
<subtitle>Earl Siachongco's blog. You may subscribe via RSS. </subtitle>
"""

FEED_DATA_END = """
</feed>
"""


class PrototypeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test_user_1", password="bruh")

        Feed.objects.create(
            name="testfeed",
            owner=self.user,
            url="http://localhost:4000/feed/shorts.xml",
            is_verified=True,
        )

    def test_non_reply_post_recognized_as_post(self):
        def customParser(url):
            return feedparser.parse(FEED_DATA_START + ITEMS_DATA + FEED_DATA_END)

        def customParser2(url):
            return feedparser.parse(
                FEED_DATA_START + ITEM_DATA + ITEMS_DATA + FEED_DATA_END
            )

        feed = Feed.objects.get(name="testfeed")

        ser.feed_update(feed=feed, parser=customParser)
        a = [x for x in Post.objects.all()]

        ser.feed_update(feed=feed, parser=customParser2)
        b = [x for x in Post.objects.all()]

        self.assertNotEqual(len(b), len(a))
