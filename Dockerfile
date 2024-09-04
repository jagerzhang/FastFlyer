FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

LABEL maintainer="Jager <jagerzhang@tencent.com>"
LABEL description="FastFlyer框架的Docker基础环境"

# 安装系统依赖
RUN sed -i 's/deb.debian.org/mirrors.cloud.tencent.com/' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install gcc g++ libsnappy-dev curl default-libmysqlclient-dev net-tools locales vim procps -y && \
    apt-get clean && \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "zh_CN.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen

# 更新pip
RUN pip3 install --upgrade pip \
    --index-url https://mirrors.cloud.tencent.com/pypi/simple/ \
    --extra-index-url https://mirrors.tencent.com/repository/pypi/tencent_pypi/simple/

# 安装依赖插件
COPY requirements.txt /tmp/requirements.txt
RUN pip install \
    --no-cache-dir \
    -r /tmp/requirements.txt \
    --index-url https://mirrors.cloud.tencent.com/pypi/simple/ \
    --extra-index-url https://mirrors.tencent.com/repository/pypi/tencent_pypi/simple/

# 安装 FastFlyer
ARG VERSION=0.9.0
ARG BUILD_NO=1
RUN echo $BUILD_NO >/dev/null && \
    pip install \
    --no-cache-dir \
    fastflyer==$VERSION \
    --index-url https://mirrors.cloud.tencent.com/pypi/simple/ \
    --extra-index-url https://mirrors.tencent.com/repository/pypi/tencent_pypi/simple/

# 调试期间每次都重新安装Fastkit，确保是最新版本
ARG BUILD_NO=1
RUN echo $BUILD_NO >/dev/null && \
    pip uninstall fastkit zhiyan-logten -y && \
    pip install \
    --no-cache-dir \
    fastkit zhiyan-logten \
    --index-url https://mirrors.cloud.tencent.com/pypi/simple/ \
    --extra-index-url https://mirrors.tencent.com/repository/pypi/tencent_pypi/simple/

WORKDIR /fastflyer

ENV TZ=Asia/Shanghai \
    TERM=linux \
    LANG=zh_CN.UTF-8 \
    LC_ALL=zh_CN.UTF-8 \
    flyer_workers=1 \
    flyer_file_log_level=warning \
    flyer_console_log_level=info \
    flyer_access_log=1 \
    flyer_reload=1 \
    flyer_rainbow_enabled=0 \
    flyer_rainbow_sync_enabled=0 \
    flyer_rainbow_sync_interval=10 \
    flyer_rainbow_host=api.rainbow.woa.com:8080 \
    flyer_rainbow_app_id=custom \
    flyer_rainbow_env_name=Default \
    flyer_rainbow_group_name=custom \
    flyer_rainbow_user_id=custom \
    flyer_rainbow_secret_key=custom \
    flyer_polaris_enabled=0 \
    flyer_polaris_namespace=Test \
    flyer_polaris_service=custom \
    flyer_polaris_token=custom \
    flyer_log_path=/fastflyer/logs

EXPOSE 8080

CMD ["fastflyer", "show_demo"]
