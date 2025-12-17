# app/models/database.py
"""
数据库模型和连接配置
"""
from typing import Optional
from pydantic import BaseModel, Field


# ==================== Pydantic 模型 ====================

class StartTaskRequest(BaseModel):
    """启动任务请求模型
    
    用于约束 POST /tasks/submit 接口的请求参数
    注意：由于包含文件上传，实际接口使用 Form 和 File 参数，此模型仅作文档说明
    """
    task_name: str = Field(..., description="任务名称，唯一标志")
    params: str = Field(..., description="参数文件（txt格式）")
    simu_prototype: str = Field(..., description="gmoncell-simu")



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
