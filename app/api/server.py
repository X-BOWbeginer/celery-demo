# app/api/server.py
"""
FastAPI 应用服务器
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from celery.result import AsyncResult

from app.config.celery_config import celery_app
from app.tasks.tasks import simulate_work, GmonCell_batch_simu
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


# ==================== API 端点 ====================

@app.get("/")
def root():
    """根路径，返回 API 信息"""
    return {
        "message": "Celery Demo API",
        "version": "0.0.1",
        "endpoints": {
            "start_task": "POST /tasks",
            "start_gmoncell_simu": "POST /tasks/gmoncell-simu",
            "get_task_status": "GET /tasks/{task_id}",
            "cancel_task": "DELETE /tasks/{task_id}",
            "health": "GET /health",
            "workers": "GET /workers",
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
                "celery": "connected",
                "workers": len(stats),
            }
        else:
            return {
                "status": "degraded",
                "celery": "no workers available",
                "workers": 0,
            }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


@app.post("/tasks", response_model=StartTaskResponse)
def start_task(req: StartTaskRequest):
    """
    启动一个新的异步任务
    
    Args:
        req: 任务请求参数
    
    Returns:
        StartTaskResponse: 包含任务 ID 和状态的响应
    """
    try:
        # 1. 创建任务目录
        task_info = task_manager.create_task_directory(task_name=req.task_name)
        
        # 2. 保存任务参数到目录
        params = {
            "seconds": req.seconds,
            "task_name": req.task_name,
        }
        task_manager.save_task_params(task_info["task_id"], params)
        
        # 3. 异步调用 Celery 任务
        task = simulate_work.apply_async(
            args=[req.seconds, req.task_name],
            task_id=None,  # 让 Celery 自动生成 task_id
            local_task_id=task_info["task_id"], # 本地任务 ID,worker 端使用
        )
        
        return StartTaskResponse(
            task_id=task.id,
            status="PENDING",
            message=f"Task '{req.task_name}' started successfully",
            local_task_id=task_info["task_id"],
            task_directory=task_info["directory"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start task: {str(e)}"
        )


@app.post("/tasks/gmoncell-simu", response_model=StartTaskResponse)
async def start_gmoncell_simu(
    file: UploadFile = File(..., description="参数文件（txt格式）"),
    task_name: str = Form(default="gmoncell_simu", description="任务名称")
):
    """
    启动 GmonCell 批量仿真任务
    
    Args:
        file: 上传的参数文件（txt格式）
        task_name: 任务名称（可选，默认为 gmoncell_simu）
    
    Returns:
        StartTaskResponse: 包含任务 ID 和状态的响应
    """
    try:
        # 1. 读取上传的文件内容
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # 2. 创建任务目录
        task_info = task_manager.create_task_directory(task_name=task_name)
        
        # 3. 保存文件内容到 params.txt
        params_file_path = task_manager.save_text_file(
            task_info["task_id"], 
            text_content, 
            filename="params.txt"
        )
        
        # 4. 异步调用 Celery 任务（暂时保持原有参数，后续会修改任务逻辑）
        task = GmonCell_batch_simu.apply_async(
            args=[10, task_name, task_info["task_id"]],  # 将 local_task_id 作为参数传递
            task_id=None,  # 让 Celery 自动生成 task_id
        )
        
        return StartTaskResponse(
            task_id=task.id,
            status="PENDING",
            message=f"GmonCell batch simulation task '{task_name}' started successfully. Params saved to {params_file_path}",
            local_task_id=task_info["task_id"],
            task_directory=task_info["directory"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start GmonCell simulation task: {str(e)}"
        )


@app.get("/tasks/{task_id}", response_model=TaskStatusResponse)
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


@app.delete("/tasks/{task_id}")
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


@app.get("/workers")
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
