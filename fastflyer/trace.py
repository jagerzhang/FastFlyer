from os import getenv
from fastflyer import config
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.kafka import KafkaInstrumentor
from opentelemetry.instrumentation.pymysql import PyMySQLInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.threading import ThreadingInstrumentor
from opentelemetry.trace import SpanKind
from fastkit.logging import get_logger

logger = get_logger("console")


class MySpanProcessor(BatchSpanProcessor):
    """自定义处理，以修复trace拆分多条上报的问题
    """

    def on_end(self, span: ReadableSpan) -> None:
        """丢弃多于的阶段trace（需配置开关：flyer_opentelemetry_reduce_request_trace=1）
        """
        is_reduce = int(getenv("flyer_opentelemetry_reduce_request_trace", 0))
        if is_reduce == 1 and span.kind == SpanKind.INTERNAL and (
                span.attributes.get('asgi.event.type')
                in ('http.request', 'http.response.start',
                    'http.response.body', 'http.disconnect')):
            return
        super().on_end(span=span)

    def paas_instrument(self):
        """paas组件上报opentelemetry
        """
        # http客户端
        if int(getenv("flyer_opentelemetry_http_enabled", 1)) == 1:
            HTTPXClientInstrumentor().instrument(
                request_hook=httpx_request_hook,
                async_request_hook=httpx_async_request_hook)
            RequestsInstrumentor().instrument(
                request_hook=httpx_request_hook,
                async_request_hook=httpx_async_request_hook)
        # kafka 客户端
        if int(getenv("flyer_opentelemetry_kafka_enabled", 1)) == 1:
            KafkaInstrumentor().instrument()
        # sqlalchemy 客户端
        if int(getenv("flyer_opentelemetry_sqlachemy_enabled", 1)) == 1:
            SQLAlchemyInstrumentor().instrument(enable_commenter=True)
        # pymysql 客户端（默认关闭，避免和SQLAlchemyInstrumentor重复）
        if int(getenv("flyer_opentelemetry_pymysql_enabled", 0)) == 1:
            PyMySQLInstrumentor().instrument()
        # Redis 客户端
        if int(getenv("flyer_opentelemetry_redis_enabled", 1)) == 1:
            RedisInstrumentor().instrument(request_hook=redis_request_hook)


def setup_opentelemetry():
    """初始化opentelemetry
    """
    if int(getenv("flyer_opentelemetry_enabled", 0)) != 1:
        return None

    tenant_id = getenv("flyer_opentelemetry_tenant_id",
                       getenv("TPS_TENANT_ID", ""))
    service_name = getenv("flyer_opentelemetry_service_name",
                          config.API_TITLE.replace(" ", ""))
    endpoint = getenv(
        "flyer_opentelemetry_endpoint",
        "http://otel-collect-proxy.zhiyan.tencent-cloud.net:4317")

    if not tenant_id:
        logger.warning("未设置租户ID，无法上报 Opentelemetry 监控数据！")
        return None

    logger.info(
        "已启用 Opentelemetry 监控数据上报：service_name=%s, tenant_id=%s, endpoint=%s",
        service_name, tenant_id, endpoint)

    resource = Resource(attributes={
        "service.name": service_name,
        "tps.tenant.id": tenant_id
    })
    tracer = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer)
    processor = MySpanProcessor(span_exporter=OTLPSpanExporter(
        endpoint=endpoint))
    tracer.add_span_processor(processor)
    LoggingInstrumentor().instrument()
    # 多线程兼容
    ThreadingInstrumentor().instrument()
    if tracer:
        processor.paas_instrument()

    return tracer


def httpx_request_hook(span, request):
    """修改httpx的spanname
    """
    method = request.method.decode() if isinstance(request.method,
                                                   bytes) else request.method
    url = str(request.url)
    span.update_name(f"{method} {url}")


async def httpx_async_request_hook(span, request):
    """修改httpx的spanname
    """
    method = request.method.decode() if isinstance(request.method,
                                                   bytes) else request.method
    url = str(request.url)
    span.update_name(f"{method} {url}")


def fastapi_server_request_hook(span, request):
    method = request.get("method")
    path = request.get("path")
    span.update_name(f"{method} {path}")


def fastapi_client_request_hook(span, request, message):
    method = request.get("method")
    path = request.get("path")
    span.update_name(f"{method} {path} http receive")


def fastapi_client_response_hook(span, request, message):
    method = request.get("method")
    path = request.get("path")
    if message.get("type") == "http.response.start":
        span.update_name(f"{method} {path} http response start")
    else:
        span.update_name(f"{method} {path} http response end")


def redis_request_hook(span, instance, args, kwargs):
    if len(args) > 1:
        operation = args[0]
        key = args[1]
        span.update_name(f"{operation} {key}")
