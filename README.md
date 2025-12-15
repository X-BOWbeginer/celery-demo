_# Celery Demo - 异步任务处理系统

基于 **Celery + FastAPI** 的分布式异步任务处理框架，采用混合部署架构：容器化服务（Redis、API、Flower）+ 主机 Worker。

## 核心特性

- **FastAPI**: 现代化 Web API 框架，自动生成交互式文档
- **Celery**: 分布式任务队列，支持异步任务处理和进度追踪
- **Flower**: 实时监控工具，提供任务和 Worker 可视化管理
- **混合部署**: 容器化基础服务，主机运行 Worker 以获得更好的性能和灵活性
- **任务管理**: 自动创建任务目录，支持文件上传和结果持久化

## 项目结构

```
celery-demo/
├── app/
│   ├── api/
│   │   └── server.py           # FastAPI 应用和路由
│   ├── config/
│   │   ├── worker_config.py    # 主机 Worker 配置
│   │   └── flower_config.py    # Flower 监控配置
│   ├── models/
│   │   └── database.py         # 数据模型定义
│   ├── tasks/
│   │   └── tasks.py            # Celery 任务定义
│   └── utils/
│       └── task_manager.py     # task管理工具
├── docker-compose.yml          # 容器服务编排
├── Dockerfile                  # 容器镜像构建
├── Makefile                    # make命令集合
├── requirements.txt            # Python 依赖
├── setup_worker_env.sh         # Worker 环境设置脚本
└── README.md                   # 项目文档
```

## 快速开始

### 前置要求

- Docker 和 Docker Compose
- Python 3.11+
- Make 工具
- ```
  # 创建worker的虚拟环境
  make worker-setup
  ```

### 一键启动所有服务

```bash
# 1. 启动所有服务（容器 + Worker）
make all
```

### 分步启动

```bash
# 1. 构建并启动容器服务（Redis、API、Flower）
make build
make up

# 2. 启动主机 Worker
make worker-start
```

### 访问服务

- **API 交互文档**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc
- **Flower 监控面板**: http://localhost:5555
- **API 根路径**: http://localhost:8000

## API 接口

### 1. 启动 GmonCell 批量仿真任务

```bash
POST /tasks/gmoncell-simu
Content-Type: multipart/form-data

参数:
- file: 参数文件（txt 格式）
- task_name: 任务名称（可选）

响应:
{
  "task_id": "celery-task-id",
  "local_task_id": "local-task-id",
  "status": "PENDING",
  "message": "Task started successfully",
  "task_directory": "/path/to/task/dir"
}
```

### 2. 查询任务状态

```bash
GET /tasks/{task_id}

响应:
{
  "task_id": "task-id",
  "status": "PROGRESS|SUCCESS|FAILURE",
  "progress": {
    "current": 5,
    "total": 10,
    "percentage": 50.0,
    "status": "Processing..."
  },
  "result": {...}  # 任务完成后的结果
}
```

### 3. 取消任务

```bash
DELETE /tasks/{task_id}

响应:
{
  "task_id": "task-id",
  "status": "REVOKED",
  "message": "Task cancelled successfully"
}
```

### 4. 查看 Worker 信息

```bash
GET /workers

响应:
{
  "stats": {...},
  "active_tasks": {...},
  "registered_tasks": {...}
}
```

### 5. 健康检查

```bash
GET /health

响应:
{
  "status": "healthy",
  "celery": "connected",
  "workers": 1
}
```

## 管理命令

### 容器服务管理

```bash
make build           # 构建 Docker 镜像
make up              # 启动容器服务
make down            # 停止容器服务
make logs            # 查看容器日志
make restart         # 重启容器服务
make clean           # 清理所有容器和数据卷
```

### 主机 Worker 管理

```bash
make worker-setup    # 设置 Worker 虚拟环境（首次运行）
make worker-start    # 启动 Worker
make worker-stop     # 停止 Worker
make worker-restart  # 重启 Worker
make worker-status   # 查看 Worker 状态
make worker-logs     # 查看 Worker 日志（实时）
```

### 其他命令

```bash
make help            # 显示所有可用命令
make all             # 启动所有服务（容器 + Worker）
```

## 架构说明

### 混合部署架构

本项目采用混合部署方案，兼顾容器化的便利性和主机运行的性能优势：

**容器化服务**:

- **Redis**: 消息代理和结果后端
- **FastAPI**: Web API 服务
- **Flower**: 监控面板

**主机服务**:

- **Celery Worker**: 在主机虚拟环境中运行，可直接访问主机资源

### 架构优势

1. **灵活性**: Worker 直接访问主机文件系统和资源
2. **调试**: 更容易调试和监控 Worker 进程
3. **隔离**: 使用虚拟环境隔离依赖，不影响系统环境

### 网络配置

- Redis 容器暴露端口 `6379` 到主机
- 容器内服务使用 `redis://redis:6379`
- 主机 Worker 使用 `redis://localhost:6379`

