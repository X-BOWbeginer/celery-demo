# app/config/worker_config.py
# 主机 Worker 配置文件
# 用于在主机上运行 Celery Worker，连接到容器中的 Redis

from celery import Celery
# from kombu import Exchange, Queue

# 主机访问容器 Redis 的配置
# 使用 localhost 或主机 IP 访问容器暴露的 Redis 端口
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"

# 创建 Celery 实例
celery_app = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Celery 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    # task_time_limit=30 * 60,  # 30 分钟硬超时
    # task_soft_time_limit=25 * 60,  # 25 分钟软超时
    # worker_prefetch_multiplier=1,
    # worker_max_tasks_per_child=1000,
)

# 导入任务模块（确保任务被注册）
def register_tasks():
    """注册所有任务模块"""
    from app.tasks import tasks  # noqa
    
# 自动注册任务
register_tasks()
