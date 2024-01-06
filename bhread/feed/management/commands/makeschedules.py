# from django_q.management.commands.qcluster import Command as BaseCommand
from django.core.management.base import BaseCommand
from feed import tasks

# from django_q.models import Schedule


# class Command(BaseCommand):
#     def handle(self, *args, **kwargs):
#         tasks.schedule_update_feeds()
#         super().handle(*args, **kwargs)


class Command(BaseCommand):
    help = "Create all schedules"

    def handle(self, *args, **kwargs):
        tasks.schedule_update_feeds()
        tasks.schedule_feed_archive()


# def ensure_schedule_updated():
#     def path(func):
#         return f"{func.__module__}.{func.__name__}"

#     Schedule.objects.update_or_create(
#         name="run_debug_print",
#         defaults={
#             "func": path(tasks.debug_print),
#             "schedule_type": Schedule.MINUTES,
#             "minutes": 5,
#         },
#     )
