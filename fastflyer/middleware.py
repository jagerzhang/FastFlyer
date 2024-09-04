# -*- coding: utf-8 -*-
import time
import json
from uuid import uuid4
import resource
from os import getenv
from fastapi.routing import APIRoute
from fastapi import Request, Response
from fastflyer.utils import get_host_ip, get_client_ip
from fastflyer import logger

host_ip = get_host_ip()


class MiddleWare(APIRoute):
    """路由中间件：记录请求日志和耗时等公共处理逻辑
    """

    async def _get_request_body(self, request: Request):
        """获取请求参数
        """
        request_body = await request.body()
        request_body = bytes.decode(request_body)

        return request_body

    async def _report_log(self, **kwargs):
        """上报智研，依赖 settings 初始化
        """
        if int(getenv("flyer_access_log", 1)) == 0:
            return

        try:
            kwargs["response"]["body"] = bytes.decode(
                kwargs["response"]["body"])

        except Exception:  # pylint: disable=broad-except
            kwargs["response"]["body"] = str(kwargs["response"]["body"])

        try:
            # 优先支持日志汇字段结构化解析
            logger.info(json.dumps(kwargs))
        except Exception:  # pylint: disable=broad-except
            logger.warning(kwargs)

    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def recorder(request: Request) -> Response:
            start_time = time.perf_counter()
            # 计算线程内存占用
            memory_usage_begin = resource.getrusage(
                resource.RUSAGE_THREAD).ru_maxrss

            # 对接NGate网关记录客户端ID
            client_id = request.headers.get("x-client-id", "")
            request_id = request.headers.get("x-request-id") or str(uuid4())
            client_ip = get_client_ip(request)

            # FastAPI 0.68.2 开始必须要传入 application/json 才识别为字典，否则报错，这里先兼容下，需要推动客户端整改后去掉
            # https://github.com/tiangolo/fastapi/releases/tag/0.65.2
            request.headers.__dict__["_list"].insert(
                0, (b"content-type", b"application/json"))
            request.headers.__dict__["_list"].insert(
                0, (b"x-request-id", request_id.encode()))

            response: Response = await original_route_handler(request)

            # 插入自定义头部
            memory_usage_end = resource.getrusage(
                resource.RUSAGE_THREAD).ru_maxrss
            memory_usage = memory_usage_end - memory_usage_begin
            latency = int((time.perf_counter() - start_time) * 1000)
            response.headers["X-Lasting-Time"] = str(latency)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Host-IP"] = host_ip
            response.headers["X-Memory-Usage"] = f"{memory_usage}KB"
            # 防御 XSS 反射型漏洞
            response.headers["X-Content-Type-Options"] = "nosniff"

            access_log = {
                "direction": "in",
                "request": {
                    "method": str(request.method),
                    "url": str(request.url),
                    "body": await self._get_request_body(request),
                    "headers": dict(request.headers.items())
                },
                "response": {
                    "status_code": response.status_code,
                    "body": response.body,
                    "headers": dict(response.headers.items())
                },
                "latency": latency,
                "clientIp": client_ip,
                "clientId": str(client_id),
                "memoryUsage": memory_usage,
                "logId": request_id
            }

            await self._report_log(**access_log)
            return response

        return recorder
