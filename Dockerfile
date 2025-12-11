FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

# 设置工作目录为 /code（项目根目录）
WORKDIR /code

# 安装系统依赖（PostgreSQL 客户端库需要）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ /code/app/

# 对外暴露端口
# 8000: FastAPI
# 5555: Flower (Celery 监控)
EXPOSE 8000 5555
