FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

LABEL maintainer="Jager <im@zhang.ge>"
LABEL description="FastFlyer框架的Docker基础镜像"

# 安装系统依赖
RUN sed -i 's/deb.debian.org/mirrors.cloud.tencent.com/' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install gcc g++ libsnappy-dev curl default-libmysqlclient-dev net-tools locales vim procps -y && \
    apt-get clean && \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && \
    echo "zh_CN.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen

# 更新pip
RUN pip3 install --upgrade pip

# 安装依赖插件
COPY requirements.txt /tmp/requirements.txt
RUN pip install \
    --no-cache-dir \
    -r /tmp/requirements.txt

# 安装 FastFlyer
ARG BUILD_NO=1
RUN echo $BUILD_NO >/dev/null && \
    pip install --upgrade \
    --no-cache-dir \
    fastflyer

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
    flyer_log_path=/fastflyer/logs

EXPOSE 8080

CMD ["fastflyer", "show", "openapi"]
