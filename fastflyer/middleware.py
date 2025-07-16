# -*- coding: utf-8 -*-
import re
import time
import json
import logging
from uuid import uuid4
import resource
from os import getenv
from fastapi.routing import APIRoute
from fastapi import Request, Response
from opentelemetry import trace
from fastflyer.utils import get_host_ip, get_client_ip
from fastflyer import logger

host_ip = get_host_ip()
# 最大body日志长度
max_body_log_length = int(getenv("flyer_max_body_log_length", "4096"))
# 最大参数集日志长度
max_params_log_length = int(getenv("flyer_max_params_log_length", "2048"))
# 最大header集日志长度
max_headers_log_length = int(getenv("flyer_max_headers_log_length", "2048"))
# 自动识别为json而无需传递content-type（如果默认，则客户端无需传递这个头部，否则必须传入才认为是JSON请求）
accept_json_without_content_type = int(getenv("flyer_accept_json_without_content_type", "0"))
# 排除日志上报的uri
exclude_uris = str(getenv("flyer_access_log_exclude_uris", "")).split(",")


class MiddleWare(APIRoute):
    """路由中间件：记录请求日志和耗时等公共处理逻辑"""

    async def _get_request_body(self, request: Request):
        """获取请求参数"""
        if request.headers.get("content-type", "").lower() == "application/json":
            try:
                return await request.json()
            except json.decoder.JSONDecodeError:
                pass

        return await request.body()

    async def _report_log(
        self,
        request_body: dict,
        request: Request,
        response: Response,
        client_ip: str,
        client_id: str,
        request_id: str,
        latency: int,
        memory_usage: int,
    ):
        """打印日志"""
        # 支持关闭日志
        if int(getenv("flyer_access_log", "1")) == 0:
            return
        
        # 支持指定不记录日志的uri
        if any(request.url.path.startswith(uri) for uri in exclude_uris):
            return

        request_body = request_body or await self._get_request_body(request)
        response_body = getattr(response, "body", None) or ""
        access_log = {
            "direction": "in",
            "request": {
                "method": str(request.method).upper(),
                "url": str(request.url),
                "body": self._dict_to_str(request_body, max_body_log_length),
                "headers": self._dict_to_str(dict(request.headers), max_headers_log_length),
                "params": self._dict_to_str(request.query_params._dict, max_params_log_length),
            },
            "response": {
                "status": response.status_code,
                "body": self._dict_to_str(response_body, max_body_log_length),
                "headers": self._dict_to_str(dict(response.headers), max_headers_log_length),
            },
            "latency": latency,
            "clientIp": client_ip,
            "clientId": str(client_id),
            "memoryUsage": memory_usage,
            "logId": request_id,
        }

        logger_report = logger.warning if response.status_code >= 400 else logger.info
        try:
            logger_report(json.dumps(access_log, ensure_ascii=False))
        except Exception:  # pylint: disable=broad-except
            logger_report(str(access_log))

    def _dict_to_str(self, data: any, max_length: int = None) -> str:
        """将字典转成字符串"""
        try:
            if isinstance(data, (dict, list, tuple)):
                result = json.dumps(data, ensure_ascii=False)
            elif isinstance(data, bytes):
                result = bytes.decode(data)
            else:
                result = str(data)
        except Exception:
            result = str(data)

        return result[:max_length] if max_length is not None else result

    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def recorder(request: Request) -> Response:
            start_time = time.perf_counter()
            # 计算线程内存占用
            memory_usage_begin = resource.getrusage(resource.RUSAGE_THREAD).ru_maxrss

            # 对接NGate网关记录客户端ID
            client_id = request.headers.get("x-client-id", "")
            request_id = request.headers.get("x-request-id") or str(uuid4())
            client_ip = get_client_ip(request)
            # FastAPI 0.68.2 开始必须要传入 application/json 才识别为字典，这里制作一个开关，方便业务选择
            # https://github.com/tiangolo/fastapi/releases/tag/0.65.2
            request_body = None
            if accept_json_without_content_type == 1:
                # 注入之前就获取 body，减少except
                request_body = await self._get_request_body(request)
                request.headers.__dict__["_list"].insert(0, (b"content-type", b"application/json"))

            # 传递 x-request-id 到上游服务
            request.headers.__dict__["_list"].insert(0, (b"x-request-id", request_id.encode()))

            # opentelemetry 植入 x-request-id
            try:
                current_span = trace.get_current_span()
                if current_span:
                    current_span.set_attribute("http.request_id", request_id)
            except Exception:  # pylint: disable=broad-except
                pass

            response: Response = await original_route_handler(request)

            # 插入自定义头部
            memory_usage_end = resource.getrusage(resource.RUSAGE_THREAD).ru_maxrss
            memory_usage = memory_usage_end - memory_usage_begin
            latency = int((time.perf_counter() - start_time) * 1000)
            response.headers["X-Lasting-Time"] = str(latency)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Host-IP"] = host_ip
            response.headers["X-Memory-Usage"] = f"{memory_usage}KB"
            # 防御 XSS 反射型漏洞
            response.headers["X-Content-Type-Options"] = "nosniff"

            # 上报日志
            await self._report_log(
                request_body,
                request,
                response,
                client_ip,
                client_id,
                request_id,
                latency,
                memory_usage,
            )

            return response

        return recorder


class AccessLogFilterMiddleware:
    def __init__(self, app, exclude_paths=None):
        self.app = app
        self.logger = logging.getLogger("uvicorn.access")
        self.exclude_uris = exclude_paths or exclude_uris

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        path = request.url.path

        # Skip logging for excluded paths
        if any(path.startswith(exclude_path) for exclude_path in self.exclude_uris):
            # Temporarily disable the uvicorn access logger
            self.logger.disabled = True

            # Create a custom send function that skips logging
            async def send_no_log(message):
                if message["type"] == "http.response.start":
                    scope["status_code"] = message["status"]
                await send(message)

            try:
                await self.app(scope, receive, send_no_log)
            finally:
                # Re-enable the logger after processing the request
                self.logger.disabled = False
            return

        # Normal processing with logging
        await self.app(scope, receive, send)
