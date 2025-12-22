# app/tasks/tasks.py
"""
Celery 异步任务模块
"""
import time
import subprocess
from celery import Task
from app.config.worker_config import celery_app
from app.config.settings import settings


class CallbackTask(Task):
    """自定义任务基类，支持进度回调"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """任务成功时的回调"""
        print(f"✅ Task {task_id} succeeded with result: {retval}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        print(f"❌ Task {task_id} failed with exception: {exc}")






@celery_app.task(bind=True, base=CallbackTask, name="tasks.GmonCell_batch_simu")
def GmonCell_batch_simu(self, seconds: int):
    """
    GmonCell 批量仿真任务
    
    Args:
        self: Celery task 实例（bind=True 时自动注入）
        seconds: 任务执行秒数
    
    Returns:
        dict: 包含任务执行结果的字典
    """
    task_id = self.request.id
    logs = []
    
    for i in range(seconds):
        time.sleep(1)
        log_msg = f"[{task_id}] progress: {i + 1}/{seconds} seconds"
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

    # 使用 Windows Python 调用批处理脚本
    try:
        # 获取 Windows Python 路径（WSL 格式）
        win_python = settings.windows_python_wsl
        # 获取批处理脚本路径（WSL 格式）
        script_path = settings.get_batch_script_path("GmonCell_batch_simu_gds_to_target.py")
        
        logs.append(f"Running script: {script_path} with task_id={task_id}")
        
        proc = subprocess.run(
            [win_python, script_path, "--task_id", str(task_id)],
            capture_output=True,
            text=True,
            check=False
        )
        logs.append(f"Script execution completed, returncode={proc.returncode}")
        if proc.stdout:
            logs.append(f"stdout: {proc.stdout}")
        if proc.stderr:
            logs.append(f"stderr: {proc.stderr}")
    except Exception as e:
        logs.append(f"Could not run batch script: {e}")

    return {
        "task_id": task_id,
        "seconds": seconds,
        "logs": logs,
        "message": "Task completed successfully",
    }

