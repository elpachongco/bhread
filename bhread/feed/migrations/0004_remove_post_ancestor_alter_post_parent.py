# Generated by Django 4.2.4 on 2023-10-26 11:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0003_alter_feed_last_scan'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='ancestor',
        ),
        migrations.AlterField(
            model_name='post',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child', to='feed.post'),
        ),
    ]
