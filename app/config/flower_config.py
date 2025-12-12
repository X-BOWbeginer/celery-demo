# app/config/flower_config.py
# Flower 监控工具的 Celery 配置文件
# 用于容器中的 Flower 服务

from celery import Celery
# from kombu import Exchange, Queue


# Celery 配置 - 容器内 Redis 连接
CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/1"

# 创建 Celery 实例
celery_app = Celery(
    "flower",
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
    # 任务路由配置
    # task_default_queue="default",
    # task_default_exchange="default",
    # task_default_routing_key="default",
    # task_queues=(
    #     Queue("default", Exchange("default"), routing_key="default"),
    #     Queue("high_priority", Exchange("high_priority"), routing_key="high_priority"),
    # ),
)

# 导入任务模块（确保任务被注册）
# 注意：这里使用延迟导入，避免循环依赖
def register_tasks():
    """注册所有任务模块"""
    from app.tasks import tasks  # noqa
    
# 自动注册任务
register_tasks()
