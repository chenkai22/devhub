from django.urls import path
from .views import UploadSessionView, ChunkUploadView, CompleteUploadView, PreviewView

urlpatterns = [
    path("uploads/", UploadSessionView.as_view(), name="create_upload"),
    path(
        "uploads/<uuid:upload_id>/chunks/",
        ChunkUploadView.as_view(),
        name="upload_chunk",
    ),
    path(
        "uploads/<uuid:upload_id>/complete/",
        CompleteUploadView.as_view(),
        name="complete_upload",
    ),
    path(
        "files/<int:file_id>/preview/",
        PreviewView.as_view(),
        name="preview",
    ),
]
