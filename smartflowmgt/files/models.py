from django.db import models
from rest_framework import serializers
from django.conf import settings
from django.utils import timezone
import uuid
from utils.filesystem import safe_join


def attachment_upload_to(instance, filename):
    # 安全生成上传路径：uploads/year/month/safe_filename
    base_path = settings.MEDIA_ROOT
    date_path = timezone.now().strftime("%Y/%m")
    target_path = safe_join(base_path, "uploads", date_path, filename)
    return target_path


class UploadSession(models.Model):
    STATUS_CHOICES = [
        ("uploading", "上传中"),
        ("completed", "已完成"),
        ("failed", "失败"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    total_chunks = models.IntegerField()
    received_chunks = models.IntegerField(default=0)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="uploading"
    )
    created_at = models.DateTimeField(auto_now_add=True)


class UploadSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UploadSession
        fields = "__all__"


class Attachment(models.Model):
    file = models.FileField(upload_to=attachment_upload_to)
    thumbnail = models.ImageField(upload_to="thumbnails/", null=True)
    session = models.OneToOneField(UploadSession, on_delete=models.CASCADE)
    converted = models.BooleanField(default=False)
