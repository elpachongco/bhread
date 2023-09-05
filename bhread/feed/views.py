from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import DeleteView
from feed import selectors as sel
from feed import services as ser
from feed import tasks

from .forms import FeedUpdateForm, PageCreateForm
from .models import Feed, Post


def home(request):
    context = {
        "posts": [],
        "favicons": [],
        "base_template": "feed/base.html",
        "url_name": "home",
    }
    for post in sel.ancestors():
        replies = sel.descendants_count(post)
        favicon = sel.favicon(post)
        context["posts"].append((ser.post_render(post), replies, favicon))
    return render(request, "feed/home.html", context)


@login_required
def feeds(request):
    context = {"base_template": "feed/base.html", "url_name": "feeds"}
    if request.method == "POST":
        f_form = FeedUpdateForm(request.POST)
        f_form.instance.added_by = request.user
        if f_form.is_valid():
            f_form.save()
            request.user.profile.feeds.add(f_form.instance)
            tasks.feed_update(f_form.instance)
            messages.success(request, "Feed created")
        else:
            messages.error(request, "Invalid Form")

    context["user_feeds"] = sel.user_feeds(request.user)

    feed_form = FeedUpdateForm
    context["feed_form"] = feed_form
    context["all_feeds"] = sel.feeds()

    return render(request, "feed/feeds.html", context)


@login_required
def feed_edit(request, pk):
    context = {"base_template": "feed/base.html"}
    feed = Feed.objects.get(id=pk)
    if request.method == "POST":
        f_form = FeedUpdateForm(request.POST, instance=feed)
        if f_form.is_valid():
            f_form.save()
            messages.success(request, "Feed Updated")
        else:
            messages.error(request, "FAILED to update feed")

    context["feed_form"] = FeedUpdateForm(instance=feed)
    return render(request, "feed/feed-edit.html", context)


@login_required
def feed_posts(request):
    context = {"posts": [], "base_template": "feed/base.html"}
    return render(request, "feed/home.html", context)


@login_required
@require_http_methods(["DELETE"])
def feed_delete(request, pk):
    try:
        Feed.objects.get(id=pk).delete()
    except Feed.DoesNotExist:
        messages.error(request, "Non-existent feed cannot be deleted")
        return redirect("feeds")

    messages.success(request, "Feed deleted")
    return redirect("feeds")


def post_children(request, pk):
    context = {"replies": [], "base_template": "feed/partial.html"}
    replies = sel.children(Post.objects.get(id=pk))
    for reply in replies:
        count = sel.descendants_count(reply)
        favicon = sel.favicon(reply)
        context["replies"].append((reply, count, favicon))
    return render(request, "feed/children.html", context)


def post_detail(request, pk=None):
    context = {"replies": [], "base_template": "feed/base.html"}
    post = Post.objects.get(id=pk)
    context["post"] = ser.post_render(post)
    context["post_favicon"] = sel.favicon(post)
    context["post_count"] = sel.descendants_count(post)

    for child in sel.children(post):
        replies = sel.descendants_count(child)
        favicon = sel.favicon(child)
        context["replies"].append((ser.post_render(child), replies, favicon))

    return render(request, "feed/detail.html", context)


def pages(request):
    context = {"base_template": "feed/base.html"}
    if request.method == "POST":
        p_form = PageCreateForm(request.POST)
        p_form.instance.user = request.user
        if p_form.is_valid():
            p_form.save()
    if request.method == "PUT":
        pass
    if request.method == "DELETE":
        pass

    context["page_form"] = PageCreateForm()
    context["user_pages"] = sel.user_pages(request.user)  # Use selector
    return render(request, "feed/pages.html", context)
