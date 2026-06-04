from app.core.settings import get_settings
from app.core.logging import setup_logging

settings = get_settings()
setup_logging()

from celery import Celery

celery_app = Celery(
    "cv_master",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
