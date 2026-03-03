from celery import Celery

from app.core.config import settings

celery_app = Celery("life_resume", include=["app.worker.tasks"])
celery_app.conf.task_always_eager = settings.celery_task_always_eager
celery_app.conf.task_routes = {"app.worker.tasks.*": {"queue": "analysis"}}
