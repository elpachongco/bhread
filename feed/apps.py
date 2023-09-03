from django.apps import AppConfig


class FeedConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "feed"

    def ready(self):
        import feed.signals
        from feed.tasks import schedule_update_feeds

        schedule_update_feeds()
