from urllib.parse import urlparse

from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from feed import selectors as sel
from feed import services as ser
from feed import tasks
from user.models import User

from .forms import FeedRegisterForm, FeedUpdateForm, PageCreateForm, VerificationForm
from .models import Feed, Post


# @cache_page(1 * 60)
def home(request, pk=None):
    context = {
        "posts": [],
        "base_template": "feed/base.html",
        "url_name": "home",
        "htmx": False,
        "js": True,
    }
    if "HX-Request" in request.headers:
        context["htmx"] = True
    if pk:
        context["js"] = False

    context["posts"] = sel.home(pk)[:6]
    return render(request, "feed/home.html", context)


# @cache_page(1 * 60)
def htmx_home(request, pk):
    context = {
        "posts": sel.home(pk)[:8],
    }
    return render(request, "feed/htmx-home.html", context)


@login_required
def feeds(request):
    context = {"base_template": "feed/base.html", "url_name": "feeds"}
    context["user_feeds"] = sel.user_feeds(request.user)
    feed_form = FeedRegisterForm
    verification_form = VerificationForm(user=request.user)
    context["feed_form"] = feed_form
    context["verification_form"] = verification_form

    if request.method == "POST":
        if "feed_submit" in request.POST:
            f_form = FeedRegisterForm(request.POST)
            f_form.instance.owner = request.user
            if f_form.is_valid():
                f_form.save()
                ser.feed_update(f_form.instance)
                messages.success(request, "Feed created")
                redirect("feeds")
            else:
                context["feed_form"] = f_form
        elif "verification_post" in request.POST:
            v_form = VerificationForm(request.POST, user=request.user)
            if v_form.is_valid():
                url = v_form.cleaned_data.get("url")
                feed = v_form.cleaned_data.get("feed")
                ser.feed_verify_url(feed, url)
                messages.success(request, "Verification post added")
                redirect("feeds")
            else:
                context["verification_form"] = v_form
                messages.error(request, "Failed to register verification post")

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


def feed_verify(request, user=""):
    user_object = None
    if User.objects.filter(username=user).exists():
        user_object = User.objects.get(username=user)

    context = {"user": user_object, "username": user}

    feed = Feed.objects.filter(owner__username=user, is_verified=True)
    if feed:
        context["verified_feeds"] = feed.all()

    return render(request, "feed/verified.html", context)


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
        favicon = ""
        context["replies"].append((reply, count, favicon))
    return render(request, "feed/children.html", context)


def post_detail(request, url=None):
    context = {"replies": [], "base_template": "feed/base.html"}
    parent = Post.objects.get(url=url)

    context["parent"] = parent
    context["parent_replies"] = sel.descendants_count(parent)
    context["children"] = Post.objects.filter(parent=parent)

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


def search(request, url):
    context = {"base_template": "feed/base.html"}
    context["results"] = Post.objects.filter(url=url)
    context["search"] = url
    return render(request, "feed/search.html", context)
