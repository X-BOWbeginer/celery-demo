.PHONY: help build up down logs restart clean test workers flower
.PHONY: worker-setup worker-start worker-stop worker-restart worker-status worker-logs

VENV_DIR = .venv_worker
VENV_PYTHON = $(VENV_DIR)/bin/python
VENV_CELERY = $(VENV_DIR)/bin/celery
WORKER_PID_FILE = /tmp/celery_worker.pid
WORKER_LOG_FILE = /tmp/celery_worker.log

help:
	@echo "Celery Demo - 可用命令:"
	@echo ""
	@echo "=== 容器服务管理 ==="
	@echo "  make build           - 构建 Docker 镜像"
	@echo "  make up              - 启动所有容器服务 (Redis, API, Flower)"
	@echo "  make down            - 停止所有容器服务"
	@echo "  make logs            - 查看容器日志"
	@echo "  make restart         - 重启所有容器服务"
	@echo "  make clean           - 清理所有容器和数据卷"
	@echo ""
	@echo "=== 主机 Worker 管理 ==="
	@echo "  make worker-setup    - 设置主机 Worker 虚拟环境"
	@echo "  make worker-start    - 启动主机 Worker"
	@echo "  make worker-stop     - 停止主机 Worker"
	@echo "  make worker-restart  - 重启主机 Worker"
	@echo "  make worker-status   - 查看主机 Worker 状态"
	@echo "  make worker-logs     - 查看主机 Worker 日志"
	@echo ""
	@echo "=== 其他 ==="
	@echo "  make test            - 运行测试脚本"
	@echo "  make all             - 启动所有服务（容器 + 主机 Worker）"

build:
	sudo docker compose build

up:
	sudo docker compose up -d
	@echo "容器服务已启动！"
	@echo "API 文档: http://localhost:8000/docs"
	@echo "Flower 监控: http://localhost:5555"
	@echo ""
	@echo "提示: 使用 'make worker-start' 启动主机 Worker"

down:
	sudo docker compose down

logs:
	sudo docker compose logs -f

restart:
	sudo docker compose restart

rebuild: down build up

clean:
	sudo docker compose down -v
	@echo "已清理所有容器和数据卷"


# ========================================
# 主机 Worker 管理命令
# ========================================

# 设置虚拟环境
worker-setup:
	@echo "设置主机 Worker 虚拟环境..."
	@bash setup_worker_env.sh
	@echo "虚拟环境设置完成！"

# 启动主机 Worker
worker-start:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "错误: 虚拟环境不存在，请先运行 'make worker-setup'"; \
		exit 1; \
	fi
	@if [ -f "$(WORKER_PID_FILE)" ]; then \
		echo "Worker 可能已在运行，请先检查状态或停止"; \
		exit 1; \
	fi
	@echo "启动主机 Worker..."
	@cd /data/workspace/celery-demo && \
		$(VENV_CELERY) -A app.config.worker_config.celery_app worker \
		--loglevel=info \
		--concurrency=1 \
		--pidfile=$(WORKER_PID_FILE) \
		--logfile=$(WORKER_LOG_FILE) \
		--detach
	@echo "主机 Worker 已启动！"
	@echo "PID 文件: $(WORKER_PID_FILE)"
	@echo "日志文件: $(WORKER_LOG_FILE)"
	@echo "查看日志: make worker-logs"

# 停止主机 Worker
worker-stop:
	@if [ ! -f "$(WORKER_PID_FILE)" ]; then \
		echo "Worker 未运行或 PID 文件不存在"; \
		exit 1; \
	fi
	@echo "停止主机 Worker..."
	@kill -TERM $$(cat $(WORKER_PID_FILE)) 2>/dev/null || true
	@rm -f $(WORKER_PID_FILE)
	@echo "主机 Worker 已停止"

# 重启主机 Worker
worker-restart: worker-stop worker-start
	@echo "主机 Worker 已重启"

# 查看主机 Worker 状态
worker-status:
	@if [ -f "$(WORKER_PID_FILE)" ]; then \
		PID=$$(cat $(WORKER_PID_FILE)); \
		if ps -p $$PID > /dev/null 2>&1; then \
			echo "主机 Worker 正在运行 (PID: $$PID)"; \
			ps -p $$PID -o pid,ppid,cmd,%mem,%cpu,etime; \
		else \
			echo "主机 Worker 未运行 (PID 文件存在但进程不存在)"; \
			rm -f $(WORKER_PID_FILE); \
		fi \
	else \
		echo "主机 Worker 未运行"; \
	fi

# 查看主机 Worker 日志
worker-logs:
	@if [ -f "$(WORKER_LOG_FILE)" ]; then \
		tail -f $(WORKER_LOG_FILE); \
	else \
		echo "日志文件不存在: $(WORKER_LOG_FILE)"; \
	fi

# 启动所有服务（容器 + 主机 Worker）
all: up worker-start
	@echo ""
	@echo "========================================"
	@echo "所有服务已启动！"
	@echo "========================================"
	@echo "API 文档: http://localhost:8000/docs"
	@echo "Flower 监控: http://localhost:5555"
	@echo "Worker 状态: make worker-status"
	@echo "Worker 日志: make worker-logs"

