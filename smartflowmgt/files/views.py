from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from .models import UploadSession, UploadSessionSerializer, Attachment
from rest_framework.response import Response
from smartflowmgt import settings
from pathlib import Path
import shutil
from django.shortcuts import get_object_or_404
from .tasks import convert_file
import pyclamd
import os
from django.core.exceptions import SuspiciousFileOperation
from utils.filesystem import safe_join
from django.http import HttpResponseBadRequest
import mimetypes
from django.http import FileResponse


def upload_file(request):
    # 获取基础存储路径（MEDIA_ROOT）
    base_dir = settings.MEDIA_ROOT

    # 用户提供的子路径（需验证）
    user_provided_path = request.POST.get("path", "")

    try:
        # 安全拼接路径
        safe_path = safe_join(base_dir, user_provided_path)
        target_path = Path(base_dir) / safe_path
    except SuspiciousFileOperation as e:
        return HttpResponseBadRequest(str(e))


# files/views.py
class UploadSessionView(APIView):
    def post(self, request):
        serializer = UploadSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.save()
        return Response({"upload_id": session.id})


class ChunkUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, upload_id):
        try:
            session = UploadSession.objects.get(id=upload_id)
        except UploadSession.DoesNotExist:
            return Response(status=404)

        chunk = request.FILES["chunk"]
        chunk_number = int(request.data["chunk_number"])

        expected_chunks = session.total_chunks
        if chunk_number >= expected_chunks:
            return Response({"error": "Invalid chunk number"}, status=400)

        # Windows兼容路径处理
        chunk_dir = Path(settings.MEDIA_ROOT) / "chunks" / str(upload_id)
        chunk_dir.mkdir(parents=True, exist_ok=True)

        chunk_path = chunk_dir / f"chunk_{chunk_number:04d}"
        with open(chunk_path, "wb") as f:
            for chunk_part in chunk.chunks():
                f.write(chunk_part)

        session.received_chunks += 1
        session.save()
        return Response({"received_chunks": session.received_chunks})


class CompleteUploadView(APIView):
    def post(self, request, upload_id):
        session = get_object_or_404(UploadSession, id=upload_id)

        # 合并文件
        chunk_dir = Path(settings.MEDIA_ROOT) / "chunks" / str(upload_id)
        final_path = Path(settings.MEDIA_ROOT) / "attachments" / session.filename

        # cd = pyclamd.ClamdAgnostic()
        # scan_result = cd.scan_file(final_path)
        # if scan_result and scan_result["status"] == "error":
        #     os.remove(final_path)
        #     return Response({"error": "File contains virus"}, status=400)

        final_dir = Path(final_path).parent
        final_dir.mkdir(parents=True, exist_ok=True)

        with open(final_path, "wb") as output:
            for chunk_file in sorted(chunk_dir.glob("chunk_*")):
                with open(chunk_file, "rb") as f:
                    output.write(f.read())

        # 清理临时文件
        shutil.rmtree(chunk_dir)

        # 创建附件记录
        attachment = Attachment.objects.create(
            file=str(final_path.relative_to(settings.MEDIA_ROOT)),  # 转换为字符串
            session=session,
        )

        # 触发异步转码
        convert_file.delay(attachment.id)

        session.status = "completed"
        session.save()
        return Response({"file_id": attachment.id})


class PreviewView(APIView):

    def get(self, request, file_id):
        attachment = get_object_or_404(Attachment, id=file_id)

        # 获取实际文件路径
        file_path = Path(settings.MEDIA_ROOT) / attachment.file.name

        # 设置MIME类型自动检测
        content_type, _ = mimetypes.guess_type(str(file_path))

        # 返回文件流响应
        response = FileResponse(open(file_path, "rb"), content_type=content_type)
        response["Content-Disposition"] = f'inline; filename="{file_path.name}"'
        return response
