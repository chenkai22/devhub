from celery import shared_task
from .models import Attachment
from django.conf import settings
from pathlib import Path
import pdf2image
from PIL import Image


@shared_task
def convert_file(attachment_id):
    attachment = Attachment.objects.get(id=attachment_id)
    file_path = attachment.file.path

    # PDF转码逻辑
    if file_path.endswith(".pdf"):
        images = pdf2image.convert_from_path(file_path, first_page=1, last_page=1)
        thumbnail_path = Path(file_path).with_suffix(".jpg")
        images[0].save(str(thumbnail_path), "JPEG")

    # 图片缩略图逻辑
    elif file_path.lower().endswith(("png", "jpg", "jpeg")):
        with Image.open(file_path) as img:
            img.thumbnail((300, 300))
            thumbnail_path = Path(file_path).parent / f"thumb_{Path(file_path).name}"
            img.save(str(thumbnail_path))

    # 更新附件记录
    attachment.thumbnail = str(thumbnail_path.relative_to(settings.MEDIA_ROOT))
    attachment.converted = True
    attachment.save()
