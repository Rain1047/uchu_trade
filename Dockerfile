# 基于 Ubuntu 20.04 镜像
FROM --platform=linux/amd64 ubuntu:20.04

# 安装基本依赖
RUN apt-get update && \
    apt-get install -y wget libc6 && \
    apt-get clean

# 下载 Miniconda 安装脚本
RUN wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh

# 执行 Miniconda 安装脚本，并清理临时文件
RUN bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh && \
    /opt/conda/bin/conda clean -afy

# 将 conda 添加到 PATH 环境变量中
ENV PATH /opt/conda/bin:$PATH

# 创建 Conda 环境并安装依赖项
RUN /opt/conda/bin/conda create -n okx-trading python=3.10 -y
RUN /opt/conda/bin/conda install -n okx-trading -c conda-forge ta-lib -y
RUN /opt/conda/bin/conda install -n okx-trading pip -y

# 激活 Conda 环境
SHELL ["/bin/bash", "-c"]
RUN source /opt/conda/bin/activate okx-trading

# 设置工作目录
WORKDIR /app

# 复制应用程序代码到容器中
COPY . ./

# 安装 Python 依赖项
RUN pip install --upgrade setuptools pip
RUN pip install mysql-connector

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
