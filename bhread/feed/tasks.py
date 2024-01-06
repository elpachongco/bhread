# Welcome mail with follow up example
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django_q.models import Schedule
from django_q.tasks import async_task, schedule
from feed import services as ser
from feed.models import Feed


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


def create_feeds_archive():
    """Create a list of feeds and write it into a static file"""
    all_feeds = list(Feed.objects.order_by("url").values_list("url", flat=True))
    if settings.DEBUG:
        file_path = settings.STATICFILES_DIRS[0] / "feeds_daily.txt"
    else:
        minutes = (1,)
        file_path = settings.STATIC_ROOT / "feeds_daily.txt"
    file_path.parent.mkdir(exist_ok=True, parents=True)
    feed_file_content = """{}""".format("\n".join(all_feeds))
    file_path.write_text(feed_file_content)


def schedule_feed_archive():
    """Schedule daily archival of feeds"""
    name = "feed_archive_daily"
    if Schedule.objects.filter(name=name).exists():
        return

    schedule(
        "feed.tasks.create_feeds_archive",
        name="feed_archive_daily",
        schedule_type=Schedule.DAILY,
        repeats=-1,
    )
