# Generated by Django 4.2.4 on 2023-09-10 15:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("feed", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="feed",
            name="verification",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="verification_post",
                to="feed.post",
            ),
        ),
    ]
