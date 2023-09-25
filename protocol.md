# The bhread protocol

The bhread protocol defines methods that allow any website to be used to participate
in a decentralized social network.

## Goals

- Simple to use
    - Must be teachable to non-tech person. Must be memorizable.
    - Must be typeable
    - Does not require installation from users
- Decentralized
    - Important Data must not be hosted at the hub
- Independent
    - Data must live even if hub dies
- Censor-free
- Familiar
    - To a degree, must be close to what people know.
- Indexable by search engine
    - Must be viewable by search engines, bots, and humans
- Understandable by non-participants
    - Must be readable. People unaware of the protocol must understand
- Uses existing technology

## The architecture

Bhread is composed of two entities a hub, and a point.

A point is any website (A blog) that has an RSS Feed.
A hub is a website where multiple points (blogs) can register to.

It's a spoke and hub model only that there could be multiple
hubs existing at a time and a point can be registered to any
number of hubs at any time.

This document defines the protocol for the hub, and the protocol for the site

## The hub protocol

- The hub is a website that collects posts from other websites.
- The hub scans of posts, and presents them in the way that this protocol defines.
- The hub must be replaceable by anyone who implements the protocol.

## The point site content protocol

The bhread protocol is composed of multiple parts with different functionality that
we think is essential for any social media platform: Discovery, Interaction, And Space.

### Discovery

Must create opportunities for allowing a user to find what they want despite millions of available posts.
Must create opportunities for allowing a blog

### Interaction

Must allow users to interact with each other (replies, threads, reposts)

1. Replies
    - What: A string "replying to" followed by an <a> tag to the post
    - The hub should display this as a reply to the link inside the <a> element.

2. Votes
    - What: A button or a set of buttons that allow the user to vote a post.
    - The hub may optionally implement any voting system for any posts.
    - Votes can be used to determine discoverability
    - Votes may be stored in a centralized database.
    - This means that each hub can have its own personality.
    - A topic in one hub may not be seen while it may trend on other hubs.

3. Repost
    - If any existing post url from a verified feed is detected in the body of a post, display that inside of the post.
    - Find only the first instance of an existing url.
    - If the url is preceded by the Reply string ("replying to"), it's a reply, not a repost.

### Space

Must allow users to be with who they want to be with (groups, subreddits).

1. Creation of group:
    - To create a group, submit a post
2. Posting to a space:
    - What: A string ""
    - Posts


### Escape

The hub must expose an endpoint that exposes data defined:
1. Vote count
