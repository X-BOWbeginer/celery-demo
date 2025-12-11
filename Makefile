.PHONY: help build up down logs restart clean test workers flower

help:
	@echo "Celery Demo - 可用命令:"
	@echo "  make build    - 构建 Docker 镜像"
	@echo "  make up       - 启动所有服务"
	@echo "  make down     - 停止所有服务"
	@echo "  make logs     - 查看日志"
	@echo "  make restart  - 重启所有服务"
	@echo "  make clean    - 清理所有容器和数据卷"
	@echo "  make test     - 运行测试脚本"

build:
	sudo docker compose build

up:
	sudo docker compose up -d
	@echo "服务已启动！"
	@echo "API 文档: http://21.6.205.138:8000/docs"
	@echo "Flower 监控: http://21.6.205.138:5555"

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

test:
	python test_api.py

