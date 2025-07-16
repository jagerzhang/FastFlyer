import os
import sys
import importlib
import traceback
import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastflyer.middleware import AccessLogFilterMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastflyer.exceptions import init_exception
from fastflyer import config, background_scheduler, asyncio_scheduler, threadpool, tracer
from fastflyer.trace import fastapi_client_request_hook, fastapi_client_response_hook, fastapi_server_request_hook
from fastflyer.base.docs import router as docs_router
from fastflyer.base.tasks import router as tasks_router
from fastflyer.authorize import authorize
from fastkit.logging import get_logger

static_dir = os.path.join(os.path.dirname(__file__), "static")
logger = get_logger(logger_name="console", log_path=config.LOG_PATH)


class FlyerAPI:
    _inst = None
    middlewares = []

    def __new__(cls, app_path, middlewares: list = None):
        """
        规避重复加载
        """
        if cls._inst is None:
            cls.app_path = app_path
            if middlewares is not None:
                cls.middlewares = middlewares
            cls._inst = cls.create_app()

        return cls._inst

    @classmethod
    def create_app(cls):
        """创建应用"""
        cls.app = FastAPI(
            title=config.API_TITLE,
            description=config.DESCRIPTION,
            version=config.VERSION,
            openapi_url=config.PREFIX + "/openapi.json",
            docs_url=None,
            redoc_url=None,
            lifespan=lifespan,
        )
        cls.app.mount(config.PREFIX + "/static", StaticFiles(directory=static_dir), name="static")
        # 应用的静态文件
        if os.path.exists(f"{cls.app_path}/../static"):
            cls.app.mount(
                config.PREFIX + "/app/static", StaticFiles(directory=f"{cls.app_path}/../static"), name="app-static"
            )
        # 加载opentelemetry
        if tracer:
            FastAPIInstrumentor.instrument_app(
                cls.app,
                tracer_provider=tracer,
                server_request_hook=fastapi_server_request_hook,
                client_request_hook=fastapi_client_request_hook,
                client_response_hook=fastapi_client_response_hook,
            )

        # 加载文档路由
        cls.app.include_router(docs_router)

        # 加载自定义中间件
        for middleware in cls.middlewares:
            cls.app.middleware("http")(middleware)

        # 屏蔽指定uri日志
        cls.app.add_middleware(
            AccessLogFilterMiddleware,
            exclude_paths=[
                "/health_check",
                f"{config.PREFIX}/health_check",
            ],
        )

        # 自动加载子项目
        cls.load_module()

        # 加载任务管理路由
        if int(os.getenv("flyer_auth_enable", "0")) == 1:
            cls.app.include_router(tasks_router, dependencies=[Depends(authorize)])

        else:
            cls.app.include_router(tasks_router)

        # 初始化异常处理
        init_exception(cls.app)
        return cls.app

    @classmethod
    def load_module(cls):
        """
        加载子项目

        Args:
            app (FastAPI): FastAPI对象
        """
        # 获取指定项目的根目录，即app目录的上一层
        root_path = os.path.dirname(cls.app_path)
        # 获取app目录名称
        app_dir = os.path.basename(cls.app_path)
        # 进入项目根目录
        sys.path.append(root_path)
        os.chdir(root_path)
        # 自动加载有路由的包
        for _dir in Path(app_dir).iterdir():
            # 不存在则跳过
            if not _dir.exists():
                continue

            # 隐藏文件夹或申明非开放文件夹或不是文件夹的跳过
            if _dir.name.startswith("_") or _dir.name.startswith(".") or not _dir.is_dir():
                continue

            try:
                sub_module = importlib.import_module(f"{app_dir}.{_dir.name}")
                # 尝试获取子模块是否启用，默认为True
                sub_module_enabled = getattr(sub_module, "__ENABLED__", True)
                if not sub_module_enabled:
                    continue

                # 跳过无路由的模块
                if not hasattr(sub_module, "router"):
                    logger.info(f"后台子项目加载成功：{_dir.name}")
                    continue

                # 开启 BasicAuth 鉴权
                if int(os.getenv("flyer_auth_enable", "0")) == 1 and getattr(sub_module, "__AUTH_ENABLED__", True):
                    cls.app.include_router(
                        sub_module.router, prefix=f"{config.PREFIX}", dependencies=[Depends(authorize)]
                    )

                else:
                    cls.app.include_router(sub_module.router, prefix=f"{config.PREFIX}")

                logger.info(f"API子项目加载成功：{_dir.name}")

            except Exception:  # pylint: disable=broad-except
                logger.error(f"API子路由加载错误：{traceback.format_exc()}")
                pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """生命周期管理"""

    def on_startup():
        """启动时执行逻辑"""
        max_threads = int(os.environ.get("flyer_threads", 5))
        logger.info(f"The Number of Threads per Worker: {max_threads}")
        loop = asyncio._get_running_loop()
        loop.set_default_executor(ThreadPoolExecutor(max_workers=max_threads))

        # 启动任务调度
        if not background_scheduler.running:
            logger.info("正在启动 Apscheduler 后台线程任务...")
            background_scheduler.start()

        # 启动异步任务调度
        if not asyncio_scheduler.running:
            logger.info("正在启动 Apscheduler 后台协程任务...")
            asyncio_scheduler.start()

    def on_shutdown():
        """关闭时执行逻辑"""
        logger.warn("收到关闭信号，FastFlyer 开始执行优雅停止逻辑...")
        # 等待一段时间再退出（最小1秒，最大60秒）
        graceful_timeout = max(min(int(os.getenv("flyer_graceful_timeout", "1")), 60), 1)
        # 关闭任务调度器
        logger.info("正在关闭 Apscheduler 定时引擎...")
        background_scheduler.shutdown(wait=True, timeout=graceful_timeout)
        asyncio_scheduler.shutdown(wait=True, timeout=graceful_timeout)
        # 关闭线程池
        logger.warning(f"正在关闭线程池，至多等待 {graceful_timeout}s ...")
        threadpool.shutdown(wait=True, timeout=graceful_timeout)
        logger.info("FastFlyer 已成功停止服务，感谢您的使用，再见！")

    on_startup()
    yield
    on_shutdown()
