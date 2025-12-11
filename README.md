# Celery Demo - 异步任务处理系统

基于 **Celery + FastAPI** 的后台长时间异步任务框架，使用 Docker Compose 部署。

## 架构说明

- **FastAPI**: Web API 框架，提供 RESTful 接口
- **Celery**: 分布式任务队列，处理异步任务
- **Redis**: 消息代理（Broker），用于任务队列
- **Flower**: Celery 监控工具，提供 Web UI

## 项目结构

### 1. 启动服务

```bash
# 构建并启动所有服务
make build
make up

# 查看日志
make logs
```

### 2. 访问服务

- **FastAPI 文档**: http://21.6.205.138:8000/docs
- **FastAPI ReDoc**: http://21.6.205.138:8000/redoc
- **Flower 监控**: http://21.6.205.138:5555
- **API 根路径**: http://21.6.205.138:8000

### 3. 停止服务

```bash
# 停止所有服务
make down

# 停止并删除数据卷
make clean
```

## API 接口

