# -*- coding: utf-8 -*-
from os import getenv


class BaseConfig:
    # 基本配置
    VERSION = getenv("flyer_version", "v1")
    PREFIX = getenv("flyer_base_url", "/flyer")
    DEVELOPER = getenv("flyer_author", "<请通过定义环境变量 flyer_author 来指定>")
    # 支持显示发布日期
    RELEASE_DATE = getenv("flyer_release_date",
                          "<请通过构建生成环境变量 flyer_release_date 来指定>")

    API_TITLE = "FastFlyer Demo"
    DESCRIPTION = f"中文名称：FastFlyer API 框架演示项目<br>\
功能说明：用于演示 FastFlyer API 开发框架的示例项目<br>\
框架源码：[Git](https://github.com/jagerzhang/fastflyer)<br>\
接口文档：[ReDoc]({PREFIX}/redoc)<br>\
快速上手：[SwaggerUI]({PREFIX}/docs)<br>\
技术支持：{DEVELOPER}<br>\
最新发布：{RELEASE_DATE}"

    # 本地日志是否开启颜色
    LOG_COLOR = True
    # 本地日志目录
    LOG_PATH = getenv("flyer_log_path", "/var/log")
    # 本地日志格式
    LOG_FORMAT = "%(color)s%(asctime)s.%(msecs)03d | %(levelname)s | %(module)s:%(lineno)d %(end_color)s| %(message)s"
    # 智研日志拓展字段，名称和logging的格式字段保持一致，支持已冒号的方式自定义别名，比如 dirname:business，则日志汇将展示 为 business
    ZHIYAN_LOG_EXT_FIELDS = ["location"]

    # 定义Body返回码的基数，默认值为0时，返回码和HTTP返回码保持一致
    STATUS_CODE_BASE = 0
    # 默认HTTP重试配置
    DEFAULT_REQUEST_RETRY_CONFIG = {
        "stop_max_attempt_number": 3,  # 最大重试 3 次
        "stop_max_delay": 60,  # 最大重试耗时 60 s
        "wait_exponential_multiplier": 2,  # 重试间隔时间倍数 2s、4s、8s...
        "wait_exponential_max": 10  # 最大重试间隔时间 10s
    }
