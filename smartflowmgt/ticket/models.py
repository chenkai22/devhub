from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.contrib.postgres.fields import ArrayField
from rest_framework import serializers
from user.models import User


class SystemConfig(models.Model):
    key = models.CharField(max_length=50, unique=True, verbose_name="配置键")
    value = models.TextField(verbose_name="配置值")

    class Meta:
        verbose_name = "系统配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.key}: {self.value}"


class Ticket(models.Model):
    ticket_code = models.CharField(max_length=12, unique=True, verbose_name="工单编号")
    title = models.CharField(max_length=100, verbose_name="主题")
    desc = models.TextField(verbose_name="描述")
    find_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="find_user_ticket"
    )
    handler = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="handler_ticket"
    )
    deadline = models.DateTimeField(verbose_name="截止时间")
    STATUS_CHOICES = (
        ("handle", "待处理"),
        ("handling", "处理中"),
        ("handled", "处理完成"),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="handle")
    attachments = models.ManyToManyField(
        "files.Attachment", verbose_name="关联附件", blank=True
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    @property
    def attachments_ids(self):
        return (
            list(self.attachments.values_list("id", flat=True))
            if self.attachments.exists()
            else []
        )


class TicketSerializer(serializers.ModelSerializer):
    deadline = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_code",
            "title",
            "desc",
            "status",
            "status_display",
            "deadline",
            "find_user",
            "handler",
            "attachments",
        ]
