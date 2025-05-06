from celery import Celery
from PIL import Image
import pdf2image
from pathlib import Path
from django.conf import settings
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartflowmgt.settings")
django.setup()

app = Celery("smartflowmgt")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

from ticket.views import WarningSettingsView

app.conf.beat_schedule = WarningSettingsView.get_celery_schedule()
