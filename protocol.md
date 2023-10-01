# The Blog Threads protocol version 0.1

The Blog Threads (BHread) protocol defines methods that allow any website to be
used to participate in a decentralized social network.

Blog threads is a social network powered by blogs. It allows bloggers to use
their blogs for interacting with other people on the internet.

For more information, read on or see
[the blog](https://blog.bhread.com/posts/about-bhread/).

## Goals of this protocol

This protocol aims to create a social network that is

- Simple to use
    - Must be teachable to non-tech person.
    - Must be memorizable.
    - Must be typeable
    - Does not require further configuration from users
- Decentralized
    - Important Data must not be hosted at one single place.
    - Data must live even if hub dies
- Censor-resistant
    - Data cannot be censored in any way unless the internet itself is censored.
- Familiar
    - To a degree, must be close to what people know.
    - Must be readable. People unaware of the protocol must understand with no
    explanation required if they visit a website participating in the protocol.
- Searchable
    - Data must be viewable by search engines, bots, and humans.

## The architecture

Bhread is composed of any number of two components:
- a hub website
- and a point website.

### Point

A point is any website that has an RSS Feed. This should mostly be blogs.
The blog may have any number of feeds as long as it doesn't repeat its posts
across feeds. Repeated posts will be handled by selecting the post that belongs
to the oldest feed registered.

### Hub

A hub is a website where multiple points (blogs) can register to.

There could be multiple hubs existing at a time and a point can be registered
to any number of hubs at any time. One example of a hub is
[bhread.com](https://bhread.com).

This document defines the protocol for the hub, and the protocol for the site.

## The hub protocol

- The hub is a website that collects feeds (RSS, Atom) submitted by anyone.
- The hub scans posts from the feed, and presents them in the way that this
protocol defines.
- The hub must be replaceable by anyone who implements the protocol.
- Multiple hubs may exist at any time.

### Submissions

- Allow anyone from the internet to add any rss feed to the hub.
    - Feed urls must be unique. If it already exists, notify contributor.
- Allow blogs to be owned by an account by verification.
    - Verify by adding bhread.com/feeds/<bhread account username>/verification
    to any part of their website and submitting it to bhread.
        - automatically detect posts that contain verification so that users can
        verify by publishing a post.
        - Understandably, users may not want to publish a new post to verify to
        some sketchy protocol, so a hub MUST allow a user to submit any page on
        the site that contains the verification string.
            - e.g. put string inside site.com/about then submit that.
            - Submission will be needed because the /about will not be in the rs feed.
    - These accounts will have more customization to their accounts
    - Customization of Display Photo
    - Disallowing their site to be on Bhread. By submitting any page on their
    domain containing the text: "bhread.com/feed/\<feedname\>/optout".

### Subscriptions

- Users must be able to subscribe to any rss feed, like any rss feed reader.
- Allow bulk submission of subscriptions from other platforms.
    - Hub Must register feeds that don't exist

### Viewing

- The hub must default to showing users only their subscriptions on the home page.
    - This is because the frontpage may be full of unwanted posts (unrelated to
    users interests, or nsfw posts).
- Users must have the ability to look at a /frontpage where the top posts from all of bhread can be found.
- Optional 'for you' page where user can find posts related to their suscriptions.

### Handling of URLs

General rule: If a url works without a trailing slash, use the version without the trailing slash.
```
google.com/
google.com
```
Use: `google.com`

## The point site content protocol

This section contains methods a website can use to participate in discussions.

The bhread protocol is composed of multiple parts with different functionality that
we think is essential for any social media platform: Discovery, Interaction, And Space.

### Discovery

Must create opportunities for allowing a user to find what they want despite millions of available posts.
Must create opportunities for allowing a blog

First, the hub will Respect a user's feed category tags.

For Atom 1.0, you need to add <category term="tag" /> to your posts. See RFC 4287 Section 4.2.2 for details.
For RSS 2.0, you need to add <category>tag</category> to your posts. See RSS 2.0 Specification for details.

### Interaction

Must allow users to interact with each other (replies, threads, reposts)

1. Posting
    - A post can be made by any website that has a feed which is registered to the hub.
    - Published posts after registration will also be posted to Bhread.
    - Post formatting will depend on how it is formatted by the RSS/Atom feed.
        - If the post truncates the post, bhread will display it as a truncated post.
        - If the post contains the full text, bhread will display the full text.
        - Bhread will allow non-harmful element tags based on
        [feedparser's sanitization](https://feedparser.readthedocs.io/en/latest/html-sanitization.html).
2. Replies
    - What: A string "replying to" followed by an \<a\> tag to the post
    - e.g. replying to [user b's article](https://example.com) This is a great article!
    - The hub should display this as a reply to the link inside the \<a\> element.
    - Replies to replies must be possible, forming a thread.
    - Users may reply to any url in the internet.
        - useful for giving feedback to a site.
        e.g.
        ```
        replying to [instructables](https://instructables.com)

        What a neat site!
        ```
3. Votes
    - What: A button or a set of buttons that allow the user to vote a post.
    - The hub may optionally implement any voting system for any posts.
    - Votes can be used to determine discoverability
    - Votes may be stored in a centralized database.
    - This means that each hub can have its own personality.
    - A topic in one hub may not be seen while it may trend on other hubs.
4. Repost
    - Useful for sharing content a user has already published without replying
    e.g.
    ```
    I wrote [this article](https://example.com) 5 years ago.
    The data needs to be updated.
    ```
    - If any existing post url from a feed is detected in the body of a post,
    display that inside of the post like a twitter repost.
    - Find only the first instance of an existing url.
    - If the url is preceded by the Reply string ("replying to"), it's a reply, not a repost.
    - A post can only be a reply or a repost.

### Space (WIP)

Must allow users to be with who they want to be with (groups, subreddits).

1. Creation of group:
    - A user may create a group where other users can post.
    - [?] A user can add any of their posts as a group page.
    - Any reply to the post will be considered as a post to the group.
    - Any reply to the group post is also considered
    - Publish a post containing the string "bhread.com/group/<username>/<groupname>"
2. Posting to a group:
    - What: A string "replying to <group url>"
    - Posts

### Escape

The hub must expose an endpoint that exposes data defined:
1. Vote count

## Related technologies

- Nostr protocol
- Webmentions
- Activitypub

## Questions

Section for important questions

- How will this handle moderation?
- How will this handle rss feeds from other content-submission websites?
- How will this prevent embedded ads?
