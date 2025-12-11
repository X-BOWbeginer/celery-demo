#!/bin/bash
# 测试任务目录创建功能

echo "🚀 测试任务目录创建功能"
echo "================================"

# 测试 1: 创建第一个任务
echo -e "\n📝 测试 1: 创建第一个任务"
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "seconds": 5,
    "task_name": "test_task_1"
  }' | jq .

sleep 2

# 测试 2: 创建第二个任务
echo -e "\n📝 测试 2: 创建第二个任务"
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "seconds": 3,
    "task_name": "test_task_2"
  }' | jq .

sleep 2

# 测试 3: 创建第三个任务
echo -e "\n📝 测试 3: 创建第三个任务"
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "seconds": 8,
    "task_name": "simulation_task"
  }' | jq .

echo -e "\n================================"
echo "✅ 测试完成！"
echo ""
echo "📂 检查任务目录："
echo "ls -la /data/workspace/EDA/schema/KQCircuits/batch_tools/simu_service/tasks/"
