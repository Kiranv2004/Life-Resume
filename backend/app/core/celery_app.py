from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "life_resume",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.worker.tasks"],
)

celery_app.conf.task_routes = {"app.worker.tasks.*": {"queue": "analysis"}}
