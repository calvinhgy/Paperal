from celery import Celery
from core import config

# 创建Celery实例
celery_app = Celery(
    "paperal",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND
)

# 配置Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# 自动发现任务
celery_app.autodiscover_tasks(["tasks"])