# 任务目录管理功能说明

## 📋 功能概述

本功能实现了在 API 接收请求时自动创建任务目录，用于存储任务相关的参数文件和数据。

## 🏗️ 架构设计

### 目录结构
```
/data/workspace/EDA/schema/KQCircuits/batch_tools/simu_service/
└── tasks/
    ├── .task_counter.json    # 任务 ID 计数器
    ├── 1/                     # 任务 1 的目录
    │   ├── metadata.json      # 任务元数据
    │   └── params.json        # 任务参数
    ├── 2/                     # 任务 2 的目录
    │   ├── metadata.json
    │   └── params.json
    └── 3/                     # 任务 3 的目录
        ├── metadata.json
        └── params.json
```

### 文件说明

#### `.task_counter.json`
记录当前最大的任务 ID，用于自增分配新任务 ID。
```json
{
  "last_task_id": 3
}
```

#### `metadata.json`
任务元数据，包含任务的基本信息。
```json
{
  "task_id": 1,
  "task_name": "test_task_1",
  "created_at": "2025-12-11T16:10:00.123456",
  "directory": "/data/simu_service/tasks/1"
}
```

#### `params.json`
任务参数，保存 API 接收到的请求参数。
```json
{
  "seconds": 10,
  "task_name": "test_task_1"
}
```

## 🔧 实现细节

### 1. 任务管理器 (`app/utils/task_manager.py`)

核心类：`TaskDirectoryManager`

**主要方法：**
- `create_task_directory()`: 创建新任务目录并分配 ID
- `get_task_directory()`: 获取指定任务的目录路径
- `save_task_params()`: 保存任务参数到文件
- `list_tasks()`: 列出所有任务

### 2. API 修改 (`app/api/server.py`)

在 `start_task()` 端点中添加了以下逻辑：

```python
# 1. 创建任务目录
task_info = task_manager.create_task_directory(task_name=req.task_name)

# 2. 保存任务参数到目录
params = {"seconds": req.seconds, "task_name": req.task_name}
task_manager.save_task_params(task_info["task_id"], params)

# 3. 启动 Celery 任务
task = simulate_work.apply_async(...)
```

### 3. Docker 挂载配置 (`docker-compose.yml`)

为 `api` 和 `worker` 容器添加了 volume 挂载：

```yaml
volumes:
  - /data/workspace/EDA/schema/KQCircuits/batch_tools/simu_service:/data/simu_service
```

这样容器内的路径 `/data/simu_service` 就映射到了宿主机的 `simu_service` 目录。

## 🚀 使用方法

### 1. 启动服务

```bash
cd /data/workspace/celery-demo
docker-compose down
docker-compose up -d
```

### 2. 创建任务

**请求示例：**
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "seconds": 10,
    "task_name": "my_simulation"
  }'
```

**响应示例：**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "PENDING",
  "message": "Task 'my_simulation' started successfully",
  "local_task_id": 1,
  "task_directory": "/data/simu_service/tasks/1"
}
```

**字段说明：**
- `task_id`: Celery 任务 ID（UUID 格式）
- `local_task_id`: 本地任务 ID（自增整数）
- `task_directory`: 任务目录路径（容器内路径）

### 3. 查看任务目录

**在宿主机上：**
```bash
ls -la /data/workspace/EDA/schema/KQCircuits/batch_tools/simu_service/tasks/
```

**在容器内：**
```bash
docker exec -it celery-api bash
ls -la /data/simu_service/tasks/
```

### 4. 查看任务文件

```bash
# 查看任务 1 的元数据
cat /data/workspace/EDA/schema/KQCircuits/batch_tools/simu_service/tasks/1/metadata.json

# 查看任务 1 的参数
cat /data/workspace/EDA/schema/KQCircuits/batch_tools/simu_service/tasks/1/params.json
```

## 🧪 测试

运行测试脚本：

```bash
chmod +x test_task_directory.sh
./test_task_directory.sh
```

测试脚本会创建 3 个任务，并显示响应结果。

## 📝 扩展使用

### 在任务中访问目录

如果需要在 Celery 任务中访问任务目录，可以这样做：

```python
from app.utils.task_manager import task_manager

@celery_app.task
def my_task(local_task_id: int):
    # 获取任务目录
    task_dir = task_manager.get_task_directory(local_task_id)
    
    # 读取参数
    params_file = task_dir / "params.json"
    with open(params_file, 'r') as f:
        params = json.load(f)
    
    # 保存结果文件
    result_file = task_dir / "result.txt"
    with open(result_file, 'w') as f:
        f.write("Task completed!")
```

### 保存额外文件

```python
# 在任务执行过程中保存日志
log_file = task_dir / "execution.log"
with open(log_file, 'a') as f:
    f.write(f"{datetime.now()}: Task started\n")

# 保存输出文件
output_file = task_dir / "output.json"
with open(output_file, 'w') as f:
    json.dump({"result": "success"}, f)
```

## ⚠️ 注意事项

1. **路径差异**：
   - 宿主机路径：`/data/workspace/EDA/schema/KQCircuits/batch_tools/simu_service`
   - 容器内路径：`/data/simu_service`

2. **权限问题**：
   - 确保 Docker 容器有权限写入挂载的目录
   - 如果遇到权限问题，可能需要调整目录权限：
     ```bash
     chmod -R 777 /data/workspace/EDA/schema/KQCircuits/batch_tools/simu_service/tasks
     ```

3. **ID 持久化**：
   - 任务 ID 通过 `.task_counter.json` 文件持久化
   - 删除此文件会导致 ID 重新从 1 开始

4. **并发安全**：
   - 当前实现使用文件锁机制，支持多进程并发创建任务
   - 在高并发场景下建议使用数据库存储 ID

## 🔄 后续优化建议

1. **数据库集成**：将任务元数据存储到数据库而非文件
2. **清理机制**：添加定期清理旧任务目录的功能
3. **文件上传**：支持通过 API 上传文件到任务目录
4. **任务查询**：添加查询任务列表和详情的 API 端点
5. **目录配置**：通过环境变量配置任务目录路径
