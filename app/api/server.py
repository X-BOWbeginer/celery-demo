# app/api/server.py
"""
FastAPI 应用服务器
"""
from typing import Literal
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from celery.result import AsyncResult

from app.config.worker_config import celery_app
from app.tasks.tasks import GmonCell_batch_simu
from app.models.database import (
    StartTaskRequest,
    StartTaskResponse,
    TaskStatusResponse,
)
from app.utils.task_manager import task_manager

app = FastAPI(
    title="Celery Demo API",
    description="基于 Celery + FastAPI 的异步任务处理系统",
    version="0.0.1",
)


@app.on_event("startup")
def clear_tasks_on_startup():
    """在 API 启动时清空 tasks 目录（由 task_manager 管理）。"""
    try:
        removed = task_manager.clear_all_tasks()
        print(f"Startup: cleared {removed} task directories")
    except Exception as e:
        print(f"Startup cleanup failed: {e}")


# ==================== API 端点 ====================

@app.get("/interface/list")
def root():
    """根路径，返回 API 信息"""
    return {
        "message": "Celery Demo API",
        "version": "0.0.1",
        "endpoints": {
            "submit_task": "POST /tasks/submit",
            "get_task_status": "GET /tasks/query/{task_id}",
            "cancel_task": "DELETE /tasks/cancel/{task_id}",
            "health": "GET /health",
            "workers": "GET /workstation",
        }
    }


@app.get("/health")
def health_check():
    """健康检查端点"""
    try:
        # 检查 Celery 是否可用
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            return {
                "status": "healthy",
                "scheduler": "connected",
                "workers": len(stats),
            }
        else:
            return {
                "status": "degraded",
                "scheduler": "no workers available",
                "workers": 0,
            }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )





@app.post("/tasks/submit", response_model=StartTaskResponse)
async def submit_task(
    task_id: str = Form(..., description="任务id，唯一标志"),
    params: UploadFile = File(..., description="参数文件（txt格式）"),
    simu_prototype: Literal["gmoncell-simu"] = Form(..., description="仿真原型，目前只能为 gmoncell-simu")
):
    """
    启动 GmonCell 批量仿真任务
    
    Args:
        task_id: 任务名称（必填，作为唯一标识符）
        params: 上传的参数文件（txt格式）
        simu_prototype: 仿真原型，值为 gmoncell-simu
    
    Returns:
        StartTaskResponse: 包含任务 ID 和状态的响应
    """
    try:
        # 0. 先用 AsyncResult 简单判断是否重复（只保留此段）
        existing = AsyncResult(task_id, app=celery_app)
        # 如果后端有明确状态（非 PENDING），视为已存在
        if existing.state and existing.state != "PENDING":
            raise HTTPException(
                status_code=409,
                detail=f"Task '{task_id}' already exists with state {existing.state}"
            )

        # 1. 读取上传的文件内容
        content = await params.read()
        text_content = content.decode('utf-8')
        
        # 2. 创建任务目录（直接使用 task_id 作为目录名）
        task_info = task_manager.create_task_directory(task_name=task_id)
        
        # 3. 保存文件内容到 params.txt
        params_file_path = task_manager.save_text_file(
            task_id, 
            text_content, 
            filename="params.txt"
        )
        
        # 4. 使用 task_id 作为 Celery 的 task_id，让 Celery 自己处理重复
        task = GmonCell_batch_simu.apply_async(
            args=[10, task_id],
            task_id=task_id,
        )
        
        return StartTaskResponse(
            task_id=task.id,  # task.id 就是 task_id
            status="PENDING",
            message=f"Task '{task_id}' started successfully",
            task_directory=task_info["directory"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start task: {str(e)}"
        )


@app.get("/tasks/query/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    """
    获取任务状态
    
    Args:
        task_id: 任务 ID
    
    Returns:
        TaskStatusResponse: 任务状态信息
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        response = TaskStatusResponse(
            task_id=task_id,
            status=task_result.state,
        )
        
        if task_result.state == "PENDING":
            response.result = None
            response.progress = None
            
        elif task_result.state == "PROGRESS":
            # 任务正在执行中
            response.progress = task_result.info
            response.result = None
            
        elif task_result.state == "SUCCESS":
            # 任务成功完成
            response.result = task_result.result
            response.progress = None
            
        elif task_result.state == "FAILURE":
            # 任务失败
            response.error = str(task_result.info)
            response.result = None
            response.progress = None
            
        else:
            # 其他状态（RETRY, REVOKED 等）
            response.result = None
            response.progress = None
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )


@app.delete("/tasks/cancel/{task_id}")
def cancel_task(task_id: str):
    """
    取消一个正在运行的任务
    
    Args:
        task_id: 任务 ID
    
    Returns:
        dict: 取消操作的结果
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.state in ["SUCCESS", "FAILURE"]:
            return {
                "task_id": task_id,
                "status": task_result.state,
                "message": f"Task already {task_result.state.lower()}, cannot cancel"
            }
        
        # 撤销任务
        task_result.revoke(terminate=True)
        
        return {
            "task_id": task_id,
            "status": "REVOKED",
            "message": "Task cancelled successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel task: {str(e)}"
        )


@app.get("/workstation")
def get_workers():
    """
    获取当前活跃的 worker 信息
    
    Returns:
        dict: Worker 统计信息
    """
    try:
        inspect = celery_app.control.inspect()
        
        stats = inspect.stats()
        active = inspect.active()
        registered = inspect.registered()
        
        return {
            "stats": stats,
            "active_tasks": active,
            "registered_tasks": registered,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get worker info: {str(e)}"
        )


def main():
    """主函数入口，用于命令行启动"""
    import uvicorn
    uvicorn.run(
        "app.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


# 直接用 uvicorn 启动
if __name__ == "__main__":
    main()
