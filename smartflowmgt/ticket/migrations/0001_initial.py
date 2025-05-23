# Generated by Django 5.2 on 2025-05-03 15:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Ticket",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ticket_code", models.CharField(max_length=20)),
                ("title", models.CharField(max_length=100, verbose_name="主题")),
                ("ticket_file", models.FileField(upload_to="", verbose_name="附件")),
                ("desc", models.TextField(verbose_name="描述")),
                ("deadline", models.DateTimeField(verbose_name="截止时间")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("handle", "待处理"),
                            ("handling", "处理中"),
                            ("handled", "处理完成"),
                        ],
                        default="handle",
                        max_length=10,
                    ),
                ),
                (
                    "find_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="find_user_ticket",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "handler",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="handler_ticket",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
