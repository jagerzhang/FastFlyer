FROM mirrors.tencent.com/nops/fastflyer:latest
LABEL maintainer="Jagerzhang<jagerzhang@tencent.com>"
LABEL description="基于 FastFlyer 开发框架构建的SRE RESTful API 服务."

WORKDIR /fastflyer

# 安装系统自定义依赖
COPY dependences.txt /tmp/
RUN apt-get install $(cat /tmp/dependences.txt | tr "\n" " ") vim -y && \
    apt-get clean

# 安装应用自定义依赖
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt --index-url https://mirrors.cloud.tencent.com/pypi/simple/  --extra-index-url https://mirrors.tencent.com/repository/pypi/tencent_pypi/simple

COPY . .

# 调试期间每次都重新安装FastFlyer 和 FastKit，确保是最新版本
ARG BUILD_NO=1
RUN echo $BUILD_NO >/dev/null && \
    pip uninstall fastkit fastflyer zhiyan-log -y && \
    pip install \
    --no-cache-dir \
    fastkit fastflyer zhiyan-log \
    --index-url https://mirrors.cloud.tencent.com/pypi/simple/ \
    --extra-index-url https://mirrors.tencent.com/repository/pypi/tencent_pypi/simple/

RUN sed -i "s/RELEASE_DATE/$(date '+%Y-%m-%d %H:%M')/" docker/docker-entrypoint.sh && \
    chmod +x /fastflyer/docker/docker-entrypoint.sh && \
    mkdir -p logs

ENTRYPOINT ["docker/docker-entrypoint.sh"]

CMD ["./start.sh"]
