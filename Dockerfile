# 使用官方 Python 3.11 的 slim 版本镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中
COPY . /app

# 安装系统依赖和 Python 包
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libmariadb-dev-compat \
        default-libmysqlclient-dev \
        build-essential \
        pkg-config \
        python3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8087

# 启动 Gunicorn
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8087", "RehabilitationManager.wsgi:application"]
