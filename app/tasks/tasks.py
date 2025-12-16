# app/tasks/tasks.py
"""
Celery 异步任务模块
"""
import time
import subprocess
from celery import Task
from app.config.worker_config import celery_app


class CallbackTask(Task):
    """自定义任务基类，支持进度回调"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """任务成功时的回调"""
        print(f"✅ Task {task_id} succeeded with result: {retval}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        print(f"❌ Task {task_id} failed with exception: {exc}")






@celery_app.task(bind=True, base=CallbackTask, name="tasks.GmonCell_batch_simu")
def GmonCell_batch_simu(self, seconds: int, task_name: str = "GmonCell_batch_simu"):
    """
    GmonCell 批量仿真任务
    
    Args:
        self: Celery task 实例（bind=True 时自动注入）
        seconds: 任务执行秒数
        task_name: 任务名称（也作为 task_id）
    
    Returns:
        dict: 包含任务执行结果的字典
    """
    logs = []
    
    for i in range(seconds):
        time.sleep(1)
        log_msg = f"[{task_name}] progress: {i + 1}/{seconds} seconds"
        logs.append(log_msg)
        
        # 更新任务状态和进度
        self.update_state(
            state="PROGRESS",
            meta={
                "current": i + 1,
                "total": seconds,
                "status": log_msg,
                "percentage": round((i + 1) / seconds * 100, 2),
            }
        )

    # 尝试在 Windows 上启动 notepad.exe 以验证从 API 能调用 Windows 可执行文件（在 WSL 环境下有效）
    try:
        # WSL 中可通过 /mnt/c/... 路径调用 Windows 可执行文件
        subprocess.Popen(["/mnt/c/Windows/System32/notepad.exe"])
        logs.append("Opened Windows notepad (attempted via /mnt/c/...)")
    except Exception as e:
        logs.append(f"Could not open Windows notepad: {e}")

    return {
        "task": task_name,
        "task_id": self.request.id,  # Celery task_id（就是 task_name）
        "seconds": seconds,
        "logs": logs,
        "message": "Task completed successfully",
    }

