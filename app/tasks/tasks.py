# app/tasks/tasks.py
"""
Celery 异步任务模块
"""
import time
from celery import Task
from app.config.celery_config import celery_app


class CallbackTask(Task):
    """自定义任务基类，支持进度回调"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """任务成功时的回调"""
        print(f"✅ Task {task_id} succeeded with result: {retval}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        print(f"❌ Task {task_id} failed with exception: {exc}")


@celery_app.task(bind=True, base=CallbackTask, name="tasks.simulate_work")
def simulate_work(self, seconds: int, task_name: str = "demo"):
    """
    模拟一个耗时任务，逐秒更新进度
    
    Args:
        self: Celery task 实例（bind=True 时自动注入）
        seconds: 任务执行秒数
        task_name: 任务名称
    
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
    
    return {
        "task": task_name,
        "seconds": seconds,
        "logs": logs,
        "message": "Task completed successfully",
    }


@celery_app.task(bind=True, name="tasks.long_running_task")
def long_running_task(self, duration: int, task_name: str = "long_task"):
    """
    长时间运行的任务，模拟复杂数据处理
    
    Args:
        self: Celery task 实例
        duration: 任务持续时间（秒）
        task_name: 任务名称
    
    Returns:
        dict: 任务结果
    """
    result = []
    
    for i in range(duration):
        time.sleep(1)
        step_result = f"Step {i + 1}/{duration} completed"
        result.append(step_result)
        
        # 更新进度
        self.update_state(
            state="PROGRESS",
            meta={
                "current": i + 1,
                "total": duration,
                "result": step_result,
                "percentage": round((i + 1) / duration * 100, 2),
            }
        )
    
    return {
        "task_name": task_name,
        "duration": duration,
        "steps": result,
        "status": "completed",
        "message": f"Processed {duration} steps successfully",
    }
