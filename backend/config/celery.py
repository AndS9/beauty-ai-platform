import os
import importlib
import pkgutil

from pathlib import Path
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY",
)

tasks_path = Path(__file__).resolve().parent.parent / "tasks"

for module in pkgutil.iter_modules([str(tasks_path)]):
    importlib.import_module(f"tasks.{module.name}")
