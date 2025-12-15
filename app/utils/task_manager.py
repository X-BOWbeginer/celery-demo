"""
任务目录管理工具
用于创建和管理任务存储目录
"""
import os
import json
from pathlib import Path
from typing import Optional
from datetime import datetime


class TaskDirectoryManager:
    """任务目录管理器"""
    
    def __init__(self, base_path: str = "/root/code/simu_service/tasks"):
        """
        初始化任务目录管理器
        
        Args:
            base_path: 任务目录的基础路径
        """
        self.base_path = Path(base_path)
        self.counter_file = self.base_path / ".task_counter.json"
        
        # 确保基础目录存在
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def _get_next_task_id(self) -> int:
        """
        获取下一个任务 ID（自增）
        
        Returns:
            int: 下一个任务 ID
        """
        if self.counter_file.exists():
            try:
                with open(self.counter_file, 'r') as f:
                    data = json.load(f)
                    current_id = data.get('last_task_id', 0)
            except (json.JSONDecodeError, IOError):
                current_id = 0
        else:
            current_id = 0
        
        # 递增 ID
        next_id = current_id + 1
        
        # 保存新的 ID
        with open(self.counter_file, 'w') as f:
            json.dump({'last_task_id': next_id}, f)
        
        return next_id
    
    def create_task_directory(self, task_name: Optional[str] = None) -> dict:
        """
        创建新的任务目录
        
        Args:
            task_name: 任务名称（可选）
        
        Returns:
            dict: 包含任务 ID、目录路径等信息的字典
        """
        # 获取新的任务 ID
        task_id = self._get_next_task_id()
        
        # 创建任务目录
        task_dir = self.base_path / str(task_id)
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建任务元数据文件
        metadata = {
            "task_id": task_id,
            "task_name": task_name or f"task_{task_id}",
            "created_at": datetime.now().isoformat(),
            "directory": str(task_dir),
        }
        
        metadata_file = task_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "task_id": task_id,
            "task_name": metadata["task_name"],
            "directory": str(task_dir),
            "created_at": metadata["created_at"],
        }
    
    def get_task_directory(self, task_id: int) -> Optional[Path]:
        """
        获取指定任务的目录路径
        
        Args:
            task_id: 任务 ID
        
        Returns:
            Path: 任务目录路径，如果不存在则返回 None
        """
        task_dir = self.base_path / str(task_id)
        return task_dir if task_dir.exists() else None
    
    def save_task_params(self, task_id: int, params: dict) -> str:
        """
        保存任务参数到文件
        
        Args:
            task_id: 任务 ID
            params: 任务参数字典
        
        Returns:
            str: 参数文件路径
        """
        task_dir = self.get_task_directory(task_id)
        if not task_dir:
            raise ValueError(f"Task directory for ID {task_id} does not exist")
        
        params_file = task_dir / "params.json"
        with open(params_file, 'w') as f:
            json.dump(params, f, indent=2)
        
        return str(params_file)
    
    def save_text_file(self, task_id: int, content: str, filename: str = "params.txt") -> str:
        """
        保存文本内容到任务目录
        
        Args:
            task_id: 任务 ID
            content: 文本内容
            filename: 文件名（默认为 params.txt）
        
        Returns:
            str: 文件路径
        """
        task_dir = self.get_task_directory(task_id)
        if not task_dir:
            raise ValueError(f"Task directory for ID {task_id} does not exist")
        
        file_path = task_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    def list_tasks(self) -> list:
        """
        列出所有任务
        
        Returns:
            list: 任务信息列表
        """
        tasks = []
        for task_dir in sorted(self.base_path.iterdir()):
            if task_dir.is_dir() and task_dir.name.isdigit():
                metadata_file = task_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        tasks.append(json.load(f))
        return tasks


# 创建全局实例
task_manager = TaskDirectoryManager()
