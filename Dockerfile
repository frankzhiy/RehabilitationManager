# 使用官方 Python 3.11 的 slim 版本镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中
COPY . /app

# 安装系统依赖和 Python 包，并配置 pip 使用国内镜像源
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libmariadb-dev-compat \
        default-libmysqlclient-dev \
        build-essential \
        pkg-config \
        python3-dev \
        ffmpeg && \
    rm -rf /var/lib/apt/lists/* && \
    # 创建 pip 配置文件，设置镜像源
    mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "index-url = https://pypi.tuna.tsinghua.edu.cn/simple" >> /root/.pip/pip.conf && \
    echo "[install]" >> /root/.pip/pip.conf && \
    echo "trusted-host = pypi.tuna.tsinghua.edu.cn" >> /root/.pip/pip.conf && \
    # 升级 pip 并安装项目依赖
    pip install --upgrade pip && \
    pip install --default-timeout=100 --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8087
EXPOSE 8088
# 启动 Gunicorn
# CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8087", "RehabilitationManager.wsgi:application"]
# 启动 WSGI 和 ASGI
CMD ["python", "start_all_services.py"]
