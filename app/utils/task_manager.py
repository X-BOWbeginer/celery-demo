"""
任务目录管理工具
用于创建和管理任务存储目录
"""
import os
import json
from pathlib import Path
from typing import Optional
from datetime import datetime
import shutil

from app.config.settings import settings


class TaskDirectoryManager:
    """任务目录管理器"""
    
    def __init__(self, base_path: str = None):
        """
        初始化任务目录管理器
        
        Args:
            base_path: 任务目录的基础路径，默认从配置文件读取（WSL格式）
        """
        # 如果未指定路径，则从配置文件读取（使用 WSL 格式路径）
        if base_path is None:
            base_path = settings.tasks_dir_wsl
        self.base_path = Path(base_path)
        
        # 确保基础目录存在
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def create_task_directory(self, task_name: str) -> dict:
        """
        创建新的任务目录（使用 task_name 作为目录名）
        
        Args:
            task_name: 任务名称（必填）
        
        Returns:
            dict: 包含任务名称、目录路径等信息的字典
        """
        # 直接使用 task_name 创建目录
        task_dir = self.base_path / task_name
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建任务元数据文件
        metadata = {
            "task_name": task_name,
            "created_at": datetime.now().isoformat(),
            "directory": str(task_dir),
        }
        
        metadata_file = task_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "task_name": task_name,
            "directory": str(task_dir),
            "created_at": metadata["created_at"],
        }
    
    def get_task_directory(self, task_name: str) -> Optional[Path]:
        """
        获取指定任务的目录路径
        
        Args:
            task_name: 任务名称
        
        Returns:
            Path: 任务目录路径，如果不存在则返回 None
        """
        task_dir = self.base_path / task_name
        return task_dir if task_dir.exists() else None
    
    def save_task_params(self, task_name: str, params: dict) -> str:
        """
        保存任务参数到文件
        
        Args:
            task_name: 任务名称
            params: 任务参数字典
        
        Returns:
            str: 参数文件路径
        """
        task_dir = self.get_task_directory(task_name)
        if not task_dir:
            raise ValueError(f"Task directory for '{task_name}' does not exist")
        
        params_file = task_dir / "params.json"
        with open(params_file, 'w') as f:
            json.dump(params, f, indent=2)
        
        return str(params_file)
    
    def save_text_file(self, task_name: str, content: str, filename: str = "params.txt") -> str:
        """
        保存文本内容到任务目录
        
        Args:
            task_name: 任务名称
            content: 文本内容
            filename: 文件名（默认为 params.txt）
        
        Returns:
            str: 文件路径
        """
        task_dir = self.get_task_directory(task_name)
        if not task_dir:
            raise ValueError(f"Task directory for '{task_name}' does not exist")
        
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
            if task_dir.is_dir() and not task_dir.name.startswith('.'):
                metadata_file = task_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        tasks.append(json.load(f))
        return tasks

    def clear_all_tasks(self) -> int:
        """
        清空 base_path 下的所有任务目录和文件。

        Returns:
            int: 被删除的顶级任务目录数量（不包括文件）。
        """
        removed_count = 0
        for child in list(self.base_path.iterdir()):
            try:
                if child.is_dir():
                    shutil.rmtree(child)
                    removed_count += 1
                else:
                    child.unlink()
            except Exception:
                # 忽略单个文件/目录删除失败，继续清理其余项
                continue
        return removed_count


# 创建全局实例
task_manager = TaskDirectoryManager()
