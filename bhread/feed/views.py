from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from feed import selectors as sel
from feed import services as ser
from feed import tasks
from user.models import User

from .forms import FeedRegisterForm, FeedUpdateForm, VerificationForm
from .models import Feed, Post, Vote


# @cache_page(5 * 60)
def home(request, pk=None):
    context = {
        "posts": [],
        "base_template": "feed/tri-column.html",
        "url_name": "home",
        "htmx": False,
        "js": True,
    }
    if "HX-Request" in request.headers:
        context["htmx"] = True
    if pk:
        context["js"] = False

    posts_qs = Post.objects.all().order_by("-date_added")
    context["posts"] = sel.posts(posts_qs)[:5]
    if request.user.is_authenticated:
        context["voted_posts"] = list(
            Vote.objects.filter(voter=request.user, post__isnull=False).values_list(
                "post", flat=True
            )
        )
    # ser.feed_update_all()
    return render(request, "feed/home.html", context)


# @cache_page(5 * 60)
def htmx_home(request, pk):
    # context = {
    #     "posts": sel.home(pk)[:8],
    # }
    context = {"posts": []}

    return render(request, "feed/htmx-home.html", context)


def feeds(request):
    context = {"base_template": "feed/tri-column.html", "url_name": "feeds"}
    # context["user_feeds"] = sel.user_feeds(request.user)
    feed_form = FeedRegisterForm
    context["feed_form"] = feed_form
    # context["verification_form"] = VerificationForm
    context["feeds"] = Feed.objects.filter(is_bozo=False)

    if request.method == "POST":
        try:
            created = ser.RegisterFeed().execute(request.POST)
        except ser.InvalidInputsError:
            messages.error(request, "That's not a valid feed!")
            return redirect("feeds")

        if created:
            messages.success(request, "Feed created")
        else:
            messages.info(request, "Feed already exists")

        return redirect("feeds")

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
            messages.warning(request, "FAILED to update feed")

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
    context = {"replies": [], "base_template": "feed/tri-column.html"}
    parent = Post.objects.get(url=url)

    context["parent"] = parent
    context["parent_replies"] = 0
    context["children"] = Post.objects.filter(parent=parent)

    return render(request, "feed/detail.html", context)


def search(request, url):
    context = {"base_template": "feed/base.html"}
    context["results"] = Post.objects.filter(url=url)
    context["search"] = url
    return render(request, "feed/search.html", context)


def groups(request):
    context = {"base_template": "feed/tri-column.html"}
    context["url_name"] = "groups"
    context["group_posts"] = Post.objects.filter(group_config__isnull=False)
    return render(request, "feed/groups.html", context)


def browse(request, pk=None):
    """lakjsfd"""
    context = {
        "posts": [],
        "base_template": "feed/base.html",
        "url_name": "browse",
        "htmx": False,
        "js": True,
    }
    return render(request, "feed/home.html", context)


def feed(request, url):
    """Allow user to subscribe"""
    context = {
        "base_template": "feed/base.html",
        "url": url,
        "subscriptions": None,
        "posts": Post.objects.filter(feed__url=url),
    }

    return render(request, "feed/feed.html", context)


# @login_required(login_url="/accounts/login")
@require_http_methods(["POST"])
def vote(request, id):
    """Allow user to vote a post"""
    context = {"id": id}
    if request.user.is_authenticated and request.method == "POST":
        post = get_object_or_404(Post, id=id)
        voted = ser.VotePost().execute({"user": request.user, "post": post})
        context["voted"] = voted
        context["votes"] = post.votes_total.count()
        if "HX-Request" in request.headers:
            return render(request, "feed/vote.html", context)
        else:
            # Redirect with anchor to the voted post
            return redirect(reverse("home") + f"#post-{id}")

    response = redirect(reverse("login") + "?next=" + reverse("home"))
    messages.info(request, "You need an account to vote")
    if not request.user.is_authenticated and "HX-Request" in request.headers:
        response = HttpResponse(401)
        response["HX-Redirect"] = reverse("login")
        # response["HX-Reswap"] = f"body"

    # NOTE: This should redirect back to post anchor after logging in.
    # NOTE: This doesn't work.
    return response
