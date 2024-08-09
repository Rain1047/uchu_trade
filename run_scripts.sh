#!/bin/bash

# shellcheck disable=SC2155
export PYTHONPATH=$(pwd)

# 获取当前脚本所在目录
SCRIPT_DIR=$(dirname "$0")

# 进入 backend 目录并运行 Python 脚本
# shellcheck disable=SC2164
cd "$SCRIPT_DIR/backend"
python main.py &

# 进入 frontend 目录并运行 npm start
# shellcheck disable=SC2164
cd "$SCRIPT_DIR/../frontend"
npm start
