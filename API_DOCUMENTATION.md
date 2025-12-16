# Celery Demo API 接口文档

## 1. 概述

本文档描述了 Celery Demo API 的所有接口定义，包括请求参数、响应参数和使用说明。

**基础信息**
- 基础URL: `http://localhost:8000`
- API版本: `v0.0.1`
- 数据格式: `JSON`

---

## 2. 接口列表

| 接口路径 | 方法 | 功能 |
|---------|------|------|
| `/` | GET | 获取API基本信息 |
| `/health` | GET | 健康检查 |
| `/tasks/gmoncell-simu` | POST | 启动GmonCell批量仿真任务 |
| `/tasks/{task_id}` | GET | 查询任务状态 |
| `/tasks/{task_id}` | DELETE | 取消任务 |
| `/workers` | GET | 查询Worker信息 |

---

## 3. 接口详细设计

### 3.1. 获取API基本信息

**接口**: `GET /`

**功能说明**: 返回API的基本信息和可用端点列表

#### 请求参数

无

#### 响应参数

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| message | string | 是 | API名称 |
| version | string | 是 | API版本号 |
| endpoints | object | 是 | 可用端点列表 |
| endpoints.start_gmoncell_simu | string | 是 | 启动仿真任务端点 |
| endpoints.get_task_status | string | 是 | 查询任务状态端点 |
| endpoints.cancel_task | string | 是 | 取消任务端点 |
| endpoints.health | string | 是 | 健康检查端点 |
| endpoints.workers | string | 是 | Worker信息端点 |

#### 响应示例

```json
{
  "message": "Celery Demo API",
  "version": "0.0.1",
  "endpoints": {
    "start_gmoncell_simu": "POST /tasks/gmoncell-simu",
    "get_task_status": "GET /tasks/{task_id}",
    "cancel_task": "DELETE /tasks/{task_id}",
    "health": "GET /health",
    "workers": "GET /workers"
  }
}
```

---

### 3.2. 健康检查

**接口**: `GET /health`

**功能说明**: 检查服务和Celery Worker的健康状态

#### 请求参数

无

#### 响应参数

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| status | string | 是 | 服务状态：<br>- `healthy`: 服务正常<br>- `degraded`: 服务降级 |
| celery | string | 是 | Celery连接状态：<br>- `connected`: 已连接<br>- `no workers available`: 无可用Worker |
| workers | int | 是 | 当前活跃的Worker数量 |

#### 响应示例

**正常状态**:
```json
{
  "status": "healthy",
  "celery": "connected",
  "workers": 2
}
```

**降级状态**:
```json
{
  "status": "degraded",
  "celery": "no workers available",
  "workers": 0
}
```

#### 错误响应

**状态码**: `503 Service Unavailable`

```json
{
  "detail": "Service unhealthy: Connection refused"
}
```

---

### 3.3. 启动GmonCell批量仿真任务

**接口**: `POST /tasks/gmoncell-simu`

**功能说明**: 上传参数文件并启动GmonCell批量仿真任务

**Content-Type**: `multipart/form-data`

#### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| file | file | 是 | 参数文件（txt格式） |
| task_name | string | 否 | 任务名称（默认为 `gmoncell_simu`） |

#### 响应参数

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| task_id | string | 是 | Celery任务ID（用于查询任务状态） |
| status | string | 是 | 任务状态：<br>- `PENDING`: 等待执行<br>- `PROGRESS`: 执行中<br>- `SUCCESS`: 成功<br>- `FAILURE`: 失败<br>- `REVOKED`: 已取消 |
| message | string | 是 | 响应提示信息 |
| local_task_id | string | 是 | 本地任务ID（用于文件管理） |
| task_directory | string | 是 | 任务工作目录路径 |

#### 请求示例

```bash
curl -X POST "http://localhost:8000/tasks/gmoncell-simu" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@params.txt" \
  -F "task_name=my_simulation"
```

#### 响应示例

**成功响应**:
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "PENDING",
  "message": "GmonCell batch simulation task 'my_simulation' started successfully. Params saved to /path/to/task/params.txt",
  "local_task_id": "20231215_143022_my_simulation",
  "task_directory": "/path/to/tasks/20231215_143022_my_simulation"
}
```

#### 错误响应

**状态码**: `500 Internal Server Error`

```json
{
  "detail": "Failed to start GmonCell simulation task: File format error"
}
```

---

### 3.4. 查询任务状态

**接口**: `GET /tasks/{task_id}`

**功能说明**: 根据任务ID查询任务的执行状态和结果

#### 请求参数

**路径参数**:

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| task_id | string | 是 | Celery任务ID |

#### 响应参数

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| task_id | string | 是 | 任务ID |
| status | string | 是 | 任务状态：<br>- `PENDING`: 等待执行<br>- `PROGRESS`: 执行中<br>- `SUCCESS`: 成功<br>- `FAILURE`: 失败<br>- `REVOKED`: 已取消 |
| result | object | 否 | 任务执行结果（仅在SUCCESS状态时返回） |
| progress | object | 否 | 任务执行进度（仅在PROGRESS状态时返回） |
| progress.current | int | 否 | 当前进度值 |
| progress.total | int | 否 | 总进度值 |
| progress.percent | float | 否 | 进度百分比 |
| progress.message | string | 否 | 进度描述信息 |
| error | string | 否 | 错误信息（仅在FAILURE状态时返回） |

#### 请求示例

```bash
curl -X GET "http://localhost:8000/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

#### 响应示例

**等待执行**:
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "PENDING",
  "result": null,
  "progress": null
}
```

**执行中**:
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "PROGRESS",
  "result": null,
  "progress": {
    "current": 5,
    "total": 10,
    "percent": 50.0,
    "message": "Processing item 5 of 10"
  }
}
```

**执行成功**:
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "SUCCESS",
  "result": {
    "total_items": 10,
    "processed": 10,
    "output_file": "/path/to/output.txt",
    "execution_time": 120.5
  },
  "progress": null
}
```

**执行失败**:
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "FAILURE",
  "result": null,
  "progress": null,
  "error": "File not found: params.txt"
}
```

#### 错误响应

**状态码**: `500 Internal Server Error`

```json
{
  "detail": "Failed to get task status: Connection error"
}
```

---

### 3.5. 取消任务

**接口**: `DELETE /tasks/{task_id}`

**功能说明**: 取消一个正在执行或等待执行的任务

**注意**: 此接口具备幂等性，重复调用不会产生副作用

#### 请求参数

**路径参数**:

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| task_id | string | 是 | Celery任务ID |

#### 响应参数

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| task_id | string | 是 | 任务ID |
| status | string | 是 | 任务状态 |
| message | string | 是 | 操作结果描述 |

#### 请求示例

```bash
curl -X DELETE "http://localhost:8000/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

#### 响应示例

**取消成功**:
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "REVOKED",
  "message": "Task cancelled successfully"
}
```

**任务已完成（无法取消）**:
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "SUCCESS",
  "message": "Task already success, cannot cancel"
}
```

**任务已失败（无法取消）**:
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "FAILURE",
  "message": "Task already failure, cannot cancel"
}
```

#### 错误响应

**状态码**: `500 Internal Server Error`

```json
{
  "detail": "Failed to cancel task: Task not found"
}
```

---

### 3.6. 查询Worker信息

**接口**: `GET /workers`

**功能说明**: 获取当前所有活跃的Celery Worker信息，包括统计数据、活跃任务和注册任务

#### 请求参数

无

#### 响应参数

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| stats | object | 是 | Worker统计信息（键为Worker名称） |
| stats.{worker_name} | object | 是 | 单个Worker的统计信息 |
| stats.{worker_name}.total | object | 是 | 任务总数统计 |
| stats.{worker_name}.pool | object | 是 | 进程池信息 |
| active_tasks | object | 是 | 当前正在执行的任务列表（键为Worker名称） |
| active_tasks.{worker_name} | array | 是 | 该Worker正在执行的任务列表 |
| registered_tasks | object | 是 | 已注册的任务类型列表（键为Worker名称） |
| registered_tasks.{worker_name} | array | 是 | 该Worker注册的任务类型列表 |

#### 请求示例

```bash
curl -X GET "http://localhost:8000/workers"
```

#### 响应示例

```json
{
  "stats": {
    "celery@worker1": {
      "total": {
        "tasks.tasks.GmonCell_batch_simu": 15
      },
      "pool": {
        "max-concurrency": 4,
        "processes": [12345, 12346, 12347, 12348],
        "max-tasks-per-child": null,
        "put-guarded-by-semaphore": true,
        "timeouts": [0, 0]
      }
    }
  },
  "active_tasks": {
    "celery@worker1": [
      {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "name": "app.tasks.tasks.GmonCell_batch_simu",
        "args": "[10, 'test_task', '20231215_143022_test']",
        "kwargs": "{}",
        "type": "app.tasks.tasks.GmonCell_batch_simu",
        "hostname": "celery@worker1",
        "time_start": 1702638622.123456,
        "acknowledged": true,
        "delivery_info": {
          "exchange": "",
          "routing_key": "celery",
          "priority": 0,
          "redelivered": false
        },
        "worker_pid": 12345
      }
    ]
  },
  "registered_tasks": {
    "celery@worker1": [
      "app.tasks.tasks.GmonCell_batch_simu",
      "celery.accumulate",
      "celery.backend_cleanup",
      "celery.chain",
      "celery.chord",
      "celery.chord_unlock",
      "celery.chunks",
      "celery.group",
      "celery.map",
      "celery.starmap"
    ]
  }
}
```

#### 错误响应

**状态码**: `500 Internal Server Error`

```json
{
  "detail": "Failed to get worker info: Connection refused"
}
```

---

## 4. 状态码说明

| 状态码 | 说明 |
|-------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

---

## 5. 任务状态说明

| 状态 | 说明 |
|-----|------|
| PENDING | 任务等待执行 |
| PROGRESS | 任务正在执行中 |
| SUCCESS | 任务执行成功 |
| FAILURE | 任务执行失败 |
| REVOKED | 任务已被取消 |
| RETRY | 任务正在重试 |

---

## 6. 使用示例

### 6.1. 完整的任务执行流程

```bash
# 1. 检查服务健康状态
curl -X GET "http://localhost:8000/health"

# 2. 启动仿真任务
RESPONSE=$(curl -X POST "http://localhost:8000/tasks/gmoncell-simu" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@params.txt" \
  -F "task_name=my_simulation")

# 3. 提取任务ID
TASK_ID=$(echo $RESPONSE | jq -r '.task_id')

# 4. 轮询查询任务状态
while true; do
  STATUS=$(curl -X GET "http://localhost:8000/tasks/$TASK_ID" | jq -r '.status')
  echo "Current status: $STATUS"
  
  if [ "$STATUS" = "SUCCESS" ] || [ "$STATUS" = "FAILURE" ]; then
    break
  fi
  
  sleep 5
done

# 5. 获取最终结果
curl -X GET "http://localhost:8000/tasks/$TASK_ID"
```

### 6.2. Python客户端示例

```python
import requests
import time

# API基础URL
BASE_URL = "http://localhost:8000"

# 1. 启动任务
with open("params.txt", "rb") as f:
    files = {"file": f}
    data = {"task_name": "my_simulation"}
    response = requests.post(f"{BASE_URL}/tasks/gmoncell-simu", files=files, data=data)
    result = response.json()
    task_id = result["task_id"]
    print(f"Task started: {task_id}")

# 2. 轮询任务状态
while True:
    response = requests.get(f"{BASE_URL}/tasks/{task_id}")
    status_data = response.json()
    status = status_data["status"]
    
    print(f"Status: {status}")
    
    if status == "PROGRESS":
        progress = status_data.get("progress", {})
        print(f"Progress: {progress.get('percent', 0)}%")
    
    if status in ["SUCCESS", "FAILURE", "REVOKED"]:
        break
    
    time.sleep(5)

# 3. 获取最终结果
if status == "SUCCESS":
    print(f"Task completed successfully!")
    print(f"Result: {status_data.get('result')}")
elif status == "FAILURE":
    print(f"Task failed: {status_data.get('error')}")
```

---

## 7. 注意事项

1. **文件上传限制**: 上传的参数文件应为txt格式，建议文件大小不超过10MB
2. **任务ID有效期**: 任务ID在任务完成后会保留一段时间（默认24小时），过期后将无法查询
3. **并发限制**: Worker的并发数由配置决定，超出并发数的任务将进入队列等待
4. **任务取消**: 只能取消PENDING或PROGRESS状态的任务，已完成或失败的任务无法取消
5. **幂等性**: 启动任务接口不具备幂等性，重复调用会创建多个任务；取消任务接口具备幂等性
6. **错误处理**: 所有接口在发生错误时都会返回包含`detail`字段的JSON响应

---

## 8. 更新日志

### v0.0.1 (2023-12-15)
- 初始版本发布
- 实现基础的任务管理功能
- 支持GmonCell批量仿真任务
- 提供健康检查和Worker监控接口
