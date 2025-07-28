import os
from celery import Celery

NODE_ENV = os.environ.get("NODE_ENV", "dev")
REDIS_HOST = os.environ.get("SDET_REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("SDET_REDIS_PORT", "6379")

celery_app = Celery(
    "doctor_octopus",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    include=["src.celery.tasks"]
)

# Configure Celery settings
celery_app.conf.update(
    task_serializer="json",
    # accept_content=["json"],
    result_serializer="json",
    timezone="EST",
    enable_utc=False,
    task_track_started=True,
    worker_redirect_stdouts_level="INFO",
    task_routes={
        "src.celery.tasks.run_main_server": {"queue": "main_server"},
        "src.celery.tasks.initialize_environment": {"queue": "main_server"},
        "src.celery.tasks.run_notification_server": {"queue": "notification"},
        "src.celery.tasks.health_check": {"queue": "monitoring"},
    },
)

# Optional: Configure periodic tasks (like health checks)
celery_app.conf.beat_schedule = {
    "health-check-every-5-minutes": {
        "task": "src.celery.tasks.health_check",
        "schedule": 300.0,  # 5 minutes
    },
}
