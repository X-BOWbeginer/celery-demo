# 主机 Worker 部署说明

本项目采用混合部署方案：
- **容器服务**: Redis、FastAPI、Flower
- **主机服务**: Celery Worker（使用虚拟环境）

## 架构优势

1. **灵活性**: Worker 在主机运行，可直接访问主机资源和文件系统
2. **性能**: 避免容器化开销，直接执行任务
3. **调试**: 更容易调试和监控 Worker 进程
4. **隔离**: 使用虚拟环境隔离依赖，不影响系统环境

## 快速开始

### 1. 首次部署

```bash
# 1. 设置主机 Worker 虚拟环境
make worker-setup

# 2. 启动容器服务（Redis、API、Flower）
make up

# 3. 启动主机 Worker
make worker-start

# 或者一键启动所有服务
make all
```

### 2. 日常使用

```bash
# 查看所有可用命令
make help

# 查看 Worker 状态
make worker-status

# 查看 Worker 日志
make worker-logs

# 重启 Worker
make worker-restart

# 停止 Worker
make worker-stop
```

## 详细说明

### 虚拟环境设置

```bash
make worker-setup
```

这个命令会：
1. 创建 Python 虚拟环境 `.venv_worker`
2. 安装所有依赖（从 `requirements.txt`）
3. 配置完成后显示使用说明

### Worker 管理

#### 启动 Worker
```bash
make worker-start
```
- Worker 以守护进程方式运行
- PID 文件: `/tmp/celery_worker.pid`
- 日志文件: `/tmp/celery_worker.log`

#### 停止 Worker
```bash
make worker-stop
```
- 优雅地停止 Worker 进程
- 清理 PID 文件

#### 重启 Worker
```bash
make worker-restart
```
- 等同于先停止再启动

#### 查看状态
```bash
make worker-status
```
显示：
- Worker 是否运行
- 进程 ID
- 内存和 CPU 使用情况
- 运行时长

#### 查看日志
```bash
make worker-logs
```
- 实时查看 Worker 日志
- 按 `Ctrl+C` 退出

### 容器服务管理

```bash
# 启动容器服务
make up

# 停止容器服务
make down

# 查看容器日志
make logs

# 重启容器服务
make restart

# 清理所有容器和数据
make clean
```

## 配置说明

### Redis 连接

- **容器内服务**: 使用 `redis://redis:6379`
- **主机 Worker**: 使用 `redis://localhost:6379`

Redis 容器暴露端口 6379 到主机，主机 Worker 通过 localhost 访问。

### Worker 配置文件

主机 Worker 使用独立的配置文件 `app/config/worker_config.py`，主要区别：
- Redis 地址使用 `localhost` 而非容器名
- 其他配置与容器版本保持一致

### 文件挂载

项目挂载了 `/data/workspace/EDA/schema/KQCircuits/batch_tools/simu_service` 目录：
- API 容器可以访问
- 主机 Worker 可以直接访问（无需挂载）

## 服务访问

- **API 文档**: http://localhost:8000/docs
- **Flower 监控**: http://localhost:5555

## 故障排查

### Worker 无法启动

1. 检查虚拟环境是否存在：
   ```bash
   ls -la .venv_worker/
   ```

2. 检查 Redis 是否运行：
   ```bash
   sudo docker compose ps
   ```

3. 手动测试连接：
   ```bash
   source .venv_worker/bin/activate
   python -c "import redis; r=redis.Redis(host='localhost', port=6379); print(r.ping())"
   ```

### Worker 运行异常

1. 查看日志：
   ```bash
   make worker-logs
   ```

2. 检查进程状态：
   ```bash
   make worker-status
   ```

3. 重启 Worker：
   ```bash
   make worker-restart
   ```

### 清理和重置

```bash
# 停止所有服务
make worker-stop
make down

# 清理容器和数据
make clean

# 删除虚拟环境（如需重建）
rm -rf .venv_worker/

# 重新开始
make worker-setup
make all
```

## 开发建议

### 修改代码后

```bash
# 重启 Worker 以加载新代码
make worker-restart

# 重启容器服务
make restart
```

### 添加新依赖

```bash
# 1. 更新 requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# 2. 重新安装依赖
source .venv_worker/bin/activate
pip install -r requirements.txt
deactivate

# 3. 重启 Worker
make worker-restart
```

## 生产环境建议

1. **使用 systemd 管理 Worker**
   - 创建 systemd service 文件
   - 实现开机自启动
   - 更好的进程管理

2. **日志轮转**
   - 配置 logrotate
   - 防止日志文件过大

3. **监控告警**
   - 使用 Flower 监控任务
   - 配置进程监控（如 Supervisor）
   - 设置告警规则

4. **资源限制**
   - 配置 Worker 并发数
   - 设置任务超时时间
   - 限制内存使用

## 文件说明

- `app/config/worker_config.py`: 主机 Worker 配置文件
- `app/config/flower_config.py`: Flower 监控工具配置文件
- `setup_worker_env.sh`: 虚拟环境设置脚本
- `create_systemd_service.sh`: Systemd 服务配置脚本（可选）
- `Makefile`: 所有管理命令
- `docker-compose.yml`: 容器服务配置
- `.venv_worker/`: 虚拟环境目录（自动创建）
