#!/usr/bin/env python3
"""
测试脚本 - 用于测试 Celery Demo API
"""

import requests
import time
import json
from typing import Optional

BASE_URL = "http://21.6.205.138:8000"

 
def print_json(data):
    """美化打印 JSON"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def health_check():
    """健康检查"""
    print("\n=== 健康检查 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print_json(response.json())
    return response.json()


def start_task(seconds: int = 10, task_name: str = "demo"):
    """启动任务"""
    print(f"\n=== 启动任务: {task_name} ({seconds}秒) ===")
    response = requests.post(
        f"{BASE_URL}/tasks",
        json={"seconds": seconds, "task_name": task_name}
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print_json(data)
    return data.get("task_id")


def get_task_status(task_id: str):
    """获取任务状态"""
    response = requests.get(f"{BASE_URL}/tasks/{task_id}")
    return response.json()


def wait_for_task(task_id: str, timeout: int = 60):
    """等待任务完成"""
    print(f"\n=== 等待任务完成: {task_id} ===")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status = get_task_status(task_id)
        print(f"\r状态: {status['status']}", end="", flush=True)
        
        if status["status"] == "PROGRESS" and status.get("progress"):
            progress = status["progress"]
            current = progress.get("current", 0)
            total = progress.get("total", 0)
            print(f"\r进度: {current}/{total} - {progress.get('status', '')}", end="", flush=True)
        
        if status["status"] in ["SUCCESS", "FAILURE", "REVOKED"]:
            print()  # 换行
            print_json(status)
            return status
        
        time.sleep(1)
    
    print("\n任务超时！")
    return None


def cancel_task(task_id: str):
    """取消任务"""
    print(f"\n=== 取消任务: {task_id} ===")
    response = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    print(f"状态码: {response.status_code}")
    print_json(response.json())


def get_workers():
    """获取 Worker 信息"""
    print("\n=== Worker 信息 ===")
    response = requests.get(f"{BASE_URL}/workers")
    print(f"状态码: {response.status_code}")
    print_json(response.json())


def test_basic_flow():
    """测试基本流程"""
    print("\n" + "="*50)
    print("测试基本流程")
    print("="*50)
    
    # 1. 健康检查
    health_check()
    
    # 2. 启动任务
    task_id = start_task(seconds=5, task_name="test_task")
    
    if task_id:
        # 3. 等待任务完成
        wait_for_task(task_id)
    
    # 4. 查看 Worker 信息
    get_workers()


def test_cancel_task():
    """测试取消任务"""
    print("\n" + "="*50)
    print("测试取消任务")
    print("="*50)
    
    # 启动一个长任务
    task_id = start_task(seconds=30, task_name="long_task")
    
    if task_id:
        # 等待 3 秒
        print("\n等待 3 秒后取消任务...")
        time.sleep(3)
        
        # 取消任务
        cancel_task(task_id)
        
        # 再次查询状态
        time.sleep(1)
        print("\n=== 取消后的任务状态 ===")
        status = get_task_status(task_id)
        print_json(status)


def test_multiple_tasks():
    """测试多个并发任务"""
    print("\n" + "="*50)
    print("测试多个并发任务")
    print("="*50)
    
    task_ids = []
    
    # 启动 3 个任务
    for i in range(3):
        task_id = start_task(seconds=5, task_name=f"task_{i+1}")
        if task_id:
            task_ids.append(task_id)
    
    # 等待所有任务完成
    print(f"\n启动了 {len(task_ids)} 个任务，等待完成...")
    
    for task_id in task_ids:
        wait_for_task(task_id, timeout=30)


def main():
    """主函数"""
    print("Celery Demo API 测试脚本")
    print("="*50)
    
    try:
        # 测试基本流程
        test_basic_flow()
        
        # 测试取消任务
        # test_cancel_task()
        
        # 测试多个并发任务
        # test_multiple_tasks()
        
        print("\n" + "="*50)
        print("测试完成！")
        print("="*50)
        
    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到 API 服务")
        print("请确保服务已启动: docker-compose up -d")
    except Exception as e:
        print(f"\n错误: {e}")


if __name__ == "__main__":
    main()
