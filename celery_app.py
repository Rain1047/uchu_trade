from celery import Celery


# 初始化 Celery 应用程序
celery_app = Celery("worker", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

# Optional: Use this for custom configuration
# celery_app.config_from_object('celery_config') # celery_config.py should contain celery configs
