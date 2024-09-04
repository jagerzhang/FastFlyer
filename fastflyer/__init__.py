# -*- coding: utf-8 -*-
from fastflyer.__info__ import *  # noqa

# 优先加载业务config，如果不存在则加载默认config
try:
    from settings import CustomConfig as config
except ImportError:
    from fastflyer.settings import BaseConfig as config

from fastkit.logging import logger  # noqa
from fastkit.httpx import status  # noqa
from fastkit.httpx import Client  # noqa
from fastkit.httpx import AsyncClient  # noqa

from .exceptions import ErrorResponse  # noqa
from .main import FlyerAPI  # noqa
from .router import APIRouter  # noqa
from fastflyer.scheduler import background_scheduler, asyncio_scheduler  # noqa

# HTTP 同步请求客户端
client = requests = Client(**config.DEFAULT_REQUEST_RETRY_CONFIG)
# HTTP 异步请求客户端
aioclient = aiorequests = AsyncClient(**config.DEFAULT_REQUEST_RETRY_CONFIG)
