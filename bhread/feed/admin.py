from django.contrib import admin

from .models import Category, Feed, Post, Vote

admin.site.register(Feed)
admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Vote)
