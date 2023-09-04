import feedparser
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Feed
from .services import get_favicon_path

# @receiver(post_save, sender=Feed)
# def signal_update_feed(sender, instance, **kwargs):
#     """On feed create, verify fields by visiting the feed itself.
#     Note: Refactor to just one update call
#     """
#     feed = Feed.objects.filter(id=instance.id)
#     d = feedparser.parse(instance.url)
#     if d.bozo:
#         feed.update(is_bozo=True)     # update does not emit post_save
#     else:
#         if hasattr(d, 'etag'):
#             feed.update(has_etag=True)
#             feed.update(etag=d.etag)
#         if hasattr(d, 'modified'):
#             feed.update(has_last_modified=True)
#             feed.update(last_modified=d.modified)
#
#     feed.update(last_scan=timezone.now())
#
#     favicon = get_favicon_path(url=instance.url)
#     feed.update(favicon=favicon)


# @receiver(post_save, sender=Feed)
# def save_feed(sender, instance, **kwargs):
#     instance.save()
