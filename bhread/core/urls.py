"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from allauth.account import views as all_auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from feed import views as feed_views
from user import views as user_views

urlpatterns = [
    path("comment-embed/<path:url>", feed_views.comment_embed, name="comment-embed"),
    path(
        "museum/", TemplateView.as_view(template_name="feed/museum.html"), name="museum"
    ),
    path(
        "welcome/",
        TemplateView.as_view(template_name="feed/welcome.html"),
        name="landing",
    ),
    path(
        "how-to-comment/",
        RedirectView.as_view(url="https://blog.bhread.com/posts/how-to-comment"),
        name="how-to-comment",
    ),
    path(
        "donate/",
        TemplateView.as_view(template_name="feed/donate.html"),
        name="donate",
    ),
    path("<int:pk>", feed_views.home, name="homenext"),
    path("<int:pk>", feed_views.home, name="homeprevious"),
    path("", feed_views.home, name="home"),
    path("all", feed_views.browse, name="browse"),
    path("groups/", feed_views.groups, name="groups"),
    path("vote/<int:id>", feed_views.vote, name="vote"),
    path("search/", feed_views.search, name="search"),
    path("accounts/", include("allauth.urls")),
    path("feed-edit/<int:pk>/", feed_views.feed_edit, name="feed-edit"),
    path("feed-delete/<int:pk>/", feed_views.feed_delete, name="feed-delete"),
    path("feeds/", feed_views.feeds, name="feeds"),
    path("feed/<path:url>", feed_views.feed, name="feed"),
    path("hx-home/<int:pk>", feed_views.htmx_home, name="hx-home"),
    path("feeds/<str:user>/verification", feed_views.feed_verify, name="proof"),
    path("verify/", feed_views.feed_verify, name="feed-verify"),
    path("login/", all_auth_views.LoginView.as_view(), name="login"),
    path(
        "about/",
        TemplateView.as_view(
            template_name="feed/about.html", extra_context={"url_name": "about"}
        ),
        name="about",
    ),
    path("feed-posts/", feed_views.feed_posts, name="userposts"),
    path("post-children/<int:pk>/", feed_views.post_children, name="children"),
    path("post/<path:url>", feed_views.post_detail, name="detail"),
    path("profile/", user_views.profile, name="profile"),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
