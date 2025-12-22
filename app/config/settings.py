# app/config/settings.py
"""
配置管理模块
负责从 config.json 加载配置，并处理 Windows 到 WSL 的路径转换
"""
import json
import os
from pathlib import Path
from typing import Optional


class Settings:
    """配置管理类"""
    
    # 配置文件路径（写死在程序中）
    # Windows 桌面路径: C:\Users\qlab\Desktop\KQCircuits\batch_service\config.json
    # WSL 路径: /mnt/c/Users/qlab/Desktop/KQCircuits/batch_service/config.json
    CONFIG_FILE_PATH = Path("/mnt/c/Users/qlab/Desktop/KQCircuits/batch_service/config.json")
    
    def __init__(self):
        self._config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        if not self.CONFIG_FILE_PATH.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.CONFIG_FILE_PATH}")
        
        with open(self.CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def reload(self):
        """重新加载配置"""
        self._config = self._load_config()
    
    @staticmethod
    def windows_to_wsl_path(win_path: str) -> str:
        """
        将 Windows 路径转换为 WSL 路径
        
        例如:
            C:\\Users\\qlab\\Desktop -> /mnt/c/Users/qlab/Desktop
            Z:\\Users\\test -> /mnt/z/Users/test
        
        Args:
            win_path: Windows 格式的路径
        
        Returns:
            str: WSL 格式的路径
        """
        if not win_path:
            return win_path
        
        # 替换反斜杠为正斜杠
        path = win_path.replace('\\', '/')
        
        # 检查是否是 Windows 驱动器路径（如 C: 或 C:/）
        if len(path) >= 2 and path[1] == ':':
            drive_letter = path[0].lower()
            rest_path = path[2:]  # 去掉 "C:"
            if rest_path.startswith('/'):
                rest_path = rest_path[1:]  # 去掉开头的斜杠
            return f"/mnt/{drive_letter}/{rest_path}"
        
        return path
    
    @staticmethod
    def wsl_to_windows_path(wsl_path: str) -> str:
        """
        将 WSL 路径转换为 Windows 路径
        
        例如:
            /mnt/c/Users/qlab/Desktop -> C:\\Users\\qlab\\Desktop
        
        Args:
            wsl_path: WSL 格式的路径
        
        Returns:
            str: Windows 格式的路径
        """
        if not wsl_path:
            return wsl_path
        
        # 检查是否是 /mnt/x/ 格式
        if wsl_path.startswith('/mnt/') and len(wsl_path) > 5:
            drive_letter = wsl_path[5].upper()
            rest_path = wsl_path[6:]  # 去掉 "/mnt/x"
            if rest_path.startswith('/'):
                rest_path = rest_path[1:]
            # 替换正斜杠为反斜杠
            rest_path = rest_path.replace('/', '\\')
            return f"{drive_letter}:\\{rest_path}"
        
        return wsl_path
    
    # ==================== 配置属性 ====================
    
    @property
    def base_dir(self) -> str:
        """获取基础目录（Windows 格式）"""
        return self._config.get("base_dir", "")
    
    @property
    def base_dir_wsl(self) -> str:
        """获取基础目录（WSL 格式）"""
        return self.windows_to_wsl_path(self.base_dir)
    
    @property
    def tasks_dir_name(self) -> str:
        """获取任务目录名称"""
        return self._config.get("tasks_dir", "tasks")
    
    @property
    def tasks_dir(self) -> str:
        """获取完整的任务目录路径（Windows 格式）"""
        return os.path.join(self.base_dir, self.tasks_dir_name)
    
    @property
    def tasks_dir_wsl(self) -> str:
        """获取完整的任务目录路径（WSL 格式）"""
        return f"{self.base_dir_wsl}/{self.tasks_dir_name}"
    
    @property
    def hfss_path(self) -> str:
        """获取 HFSS 可执行文件路径（Windows 格式）"""
        return self._config.get("hfss_path", "")
    
    @property
    def hfss_path_wsl(self) -> str:
        """获取 HFSS 可执行文件路径（WSL 格式）"""
        return self.windows_to_wsl_path(self.hfss_path)
    
    # ==================== 批处理脚本配置（写死） ====================
    
    # Windows Python 路径（写死）
    WINDOWS_PYTHON_PATH = "C:\\Python39\\python.exe"
    
    # 批处理脚本目录（Windows 格式，写死）
    BATCH_SCRIPT_DIR = "C:\\Users\\qlab\\Desktop\\KQCircuits\\batch_service\\batch_simu_script"
    
    @property
    def windows_python_wsl(self) -> str:
        """获取 Windows Python 路径（WSL 格式）"""
        return self.windows_to_wsl_path(self.WINDOWS_PYTHON_PATH)
    
    @property
    def batch_script_dir_wsl(self) -> str:
        """获取批处理脚本目录（WSL 格式）"""
        return self.windows_to_wsl_path(self.BATCH_SCRIPT_DIR)
    
    def get_batch_script_path(self, script_name: str, wsl_format: bool = True) -> str:
        """
        获取批处理脚本完整路径
        
        Args:
            script_name: 脚本文件名，如 "GmonCell_batch_simu_gds_to_target.py"
            wsl_format: 是否返回 WSL 格式路径
        
        Returns:
            str: 脚本完整路径
        """
        if wsl_format:
            return f"{self.batch_script_dir_wsl}/{script_name}"
        else:
            return f"{self.BATCH_SCRIPT_DIR}\\{script_name}"
    
    @property
    def gds_dir_path(self) -> str:
        """获取 GDS 目录路径"""
        return self._config.get("GDS_dir_path", "GDS")
    
    @property
    def revert_gds_dir_path(self) -> str:
        """获取恢复 GDS 目录路径"""
        return self._config.get("revert_GDS_dir_path", "valid_layout")
    
    @property
    def invalid_gds_dir_path(self) -> str:
        """获取无效 GDS 目录路径"""
        return self._config.get("invalid_GDS_dir_path", "invalid_layout")
    
    @property
    def aedt_source_name(self) -> str:
        """获取 AEDT 源文件名"""
        return self._config.get("aedt_source_name", "project.aedt")
    
    @property
    def aedt_target_path(self) -> str:
        """获取 AEDT 目标路径"""
        return self._config.get("aedt_target_path", "HFSS_Simulation")
    
    # ==================== Redis/Celery 配置（写死，不从 config.json 读取） ====================
    
    # Redis 配置 - 直接写死
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    
    @property
    def celery_broker_url(self) -> str:
        """获取 Celery Broker URL（写死）"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    @property
    def celery_result_backend(self) -> str:
        """获取 Celery Result Backend URL（写死）"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"
    
    def get(self, key: str, default=None):
        """获取原始配置值"""
        return self._config.get(key, default)


# 创建全局配置实例
settings = Settings()
