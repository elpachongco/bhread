def make_item(title="test_title_1", link="http://testing.com", content="test content"):
    item = f"""
    <entry>
    <title type="html">{title}</title>
    <link href="{link}" rel="alternate" type="text/html" title="{title}" />
    <published>2023-09-08T00:40:09+08:00</published>
    <updated>2023-09-08T00:40:09+08:00</updated>
    <id>{link}</id>
    <content type="html" xml:base="{link}">
        {content}
    </content>
    <author>
    <name></name>
    </author>
    <summary type="html">{content}</summary>
    </entry>
    """
    return item


def make_feed(items=[], link="", home_link="", title="test_feed"):
    start = f"""<?xml version="1.0" encoding="utf-8"?>
    <feed
    xmlns="http://www.w3.org/2005/Atom" >
    <generator uri="https://jekyllrb.com/" version="3.8.6">Jekyll</generator>
    <link href="{link}" rel="self" type="application/atom+xml" />
    <link href="{home_link}" rel="alternate" type="text/html" />
    <updated>2023-09-13T18:16:34+08:00</updated>
    <id>{link}</id>
    <title type="html">{title}</title>
    <subtitle>Earl Siachongco's blog. You may subscribe via RSS. </subtitle>
    """
    end = """
    </feed>
    """
    return start + "".join(items) + end
