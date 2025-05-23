# Generated by Django 5.2 on 2025-05-05 21:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ticket", "0002_remove_ticket_ticket_file_ticket_attachments_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="create_time",
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(2025, 5, 4, 0, 0),
                verbose_name="创建时间",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ticket",
            name="update_time",
            field=models.DateTimeField(auto_now=True, verbose_name="更新时间"),
        ),
    ]
