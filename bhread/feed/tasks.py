# Welcome mail with follow up example
from datetime import timedelta

from django.utils import timezone
from django_q.models import Schedule
from django_q.tasks import async_task, schedule
from feed import services as ser


def schedule_update_feeds():
    """Create a schedule for updating feeds.
    This task is registered in apps.py"""
    name = "feed_update_all"
    if Schedule.objects.filter(name=name).exists():
        return

    schedule(
        "feed.services.feed_update_all",
        name="feed_update_all",
        schedule_type=Schedule.MINUTES,
        minutes=1,
        repeats=-1,
    )


def feed_update(feed):
    async_task("feed.services.UpdateFeed.execute", {"feed": feed})
