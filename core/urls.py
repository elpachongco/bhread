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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView

from feed import views as feed_views
from user import views as user_views

urlpatterns = [
    path("", feed_views.home, name="home"),
    path("pages/", feed_views.pages, name="pages"),
    path("feed-edit/<int:pk>/", feed_views.feed_edit, name="feed-edit"),
    path("feed-delete/<int:pk>/", feed_views.feed_delete, name="feed-delete"),
    path("feeds/", feed_views.feeds, name="feeds"),
    path(
        "about/",
        TemplateView.as_view(
            template_name="feed/about.html", extra_context={"url_name": "about"}
        ),
        name="about",
    ),
    path("feed-posts/", feed_views.feed_posts, name="userposts"),
    path("post-children/<int:pk>/", feed_views.post_children, name="children"),
    path("post/<int:pk>/", feed_views.post_detail, name="detail"),
    path("profile/", user_views.profile, name="profile"),
    path("register/", user_views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="user/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="user/logout.html"),
        name="logout",
    ),
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
