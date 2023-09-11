from django_q.management.commands.qcluster import Command as BaseCommand
from feed import tasks

# from django_q.models import Schedule


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        tasks.schedule_update_feeds()
        super().handle(*args, **kwargs)


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
