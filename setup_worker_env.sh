#!/bin/bash
# setup_worker_env.sh
# 设置主机 Worker 虚拟环境的脚本

set -e

VENV_DIR=".venv_worker"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=========================================="
echo "设置 Celery Worker 虚拟环境"
echo "=========================================="

# 检查是否已存在虚拟环境
if [ -d "$VENV_DIR" ]; then
    echo "虚拟环境已存在: $VENV_DIR"
    read -p "是否删除并重新创建? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "删除旧的虚拟环境..."
        rm -rf "$VENV_DIR"
    else
        echo "使用现有虚拟环境"
        exit 0
    fi
fi

# 创建虚拟环境
echo "创建虚拟环境: $VENV_DIR"
python3 -m venv "$VENV_DIR"

# 激活虚拟环境
echo "激活虚拟环境..."
source "$VENV_DIR/bin/activate"

# 升级 pip
# echo "升级 pip..."
# pip install --upgrade pip

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

echo "=========================================="
echo "虚拟环境设置完成！"
echo "=========================================="
echo ""
echo "使用方法："
echo "  1. 激活虚拟环境: source $VENV_DIR/bin/activate"
echo "  2. 启动 Worker: make worker-start"
echo "  3. 停止 Worker: make worker-stop"
echo "  4. 查看 Worker 状态: make worker-status"
echo "  5. 退出虚拟环境: deactivate"
echo ""
