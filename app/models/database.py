# app/models/database.py
"""
数据库模型和连接配置
"""
from typing import Optional
from pydantic import BaseModel


# ==================== Pydantic 模型 ====================

class StartTaskRequest(BaseModel):
    """启动任务请求模型"""
    seconds: int = 10
    task_name: str = "demo"
    
    class Config:
        json_schema_extra = {
            "example": {
                "seconds": 10,
                "task_name": "demo"
            }
        }


class StartTaskResponse(BaseModel):
    """启动任务响应模型"""
    task_id: str
    status: str
    message: str
    task_directory: Optional[str] = None  # 任务目录路径


class TaskStatusResponse(BaseModel):
    """任务状态响应模型"""
    task_id: str
    status: str  # PENDING, PROGRESS, SUCCESS, FAILURE, REVOKED
    result: Optional[dict] = None
    progress: Optional[dict] = None
    error: Optional[str] = None
