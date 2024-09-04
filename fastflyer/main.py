import os
import sys
import time
import importlib
import traceback
import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastflyer.exceptions import init_exception
from fastflyer import config, background_scheduler, asyncio_scheduler
from fastflyer.docs import router as docs
from fastflyer.authorize import authorize
from fastkit.logging import get_logger

static_dir = os.path.join(os.path.dirname(__file__), "static")
logger = get_logger(logger_name="console", log_path=config.LOG_PATH)


class FlyerAPI:
    _inst = None

    def __new__(cls, app_path):
        """
        规避重复加载
        """
        if cls._inst is None:
            cls.app_path = app_path
            cls._inst = cls.create_app()

        return cls._inst

    @classmethod
    def create_app(cls):
        """创建应用"""
        cls.app = FastAPI(title=config.API_TITLE,
                          description=config.DESCRIPTION,
                          version=config.VERSION,
                          openapi_url=config.PREFIX + "/openapi.json",
                          docs_url=None,
                          redoc_url=None)
        cls.app.mount(config.PREFIX + "/static",
                      StaticFiles(directory=static_dir),
                      name="static")
        cls.app.include_router(docs)
        # 自动加载子项目
        cls.load_module()
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
        for dir in Path(app_dir).iterdir():
            # 不存在则跳过
            if not dir.exists():
                continue

            # 隐藏文件夹或申明非开放文件夹或不是文件夹的跳过
            if dir.name.startswith("_") or dir.name.startswith(
                    ".") or not dir.is_dir():
                continue

            try:
                # eval(f"import {app_dir}.{dir.name}")
                sub_module = importlib.import_module(f"{app_dir}.{dir.name}")
                # 尝试获取子模块是否启用，默认为True
                sub_module_enabled = getattr(sub_module, "__ENABLED__", True)
                if not sub_module_enabled:
                    continue

                # 开启 BasicAuth 鉴权
                if int(os.getenv("flyer_auth_enable", 0)) == 1:
                    cls.app.include_router(sub_module.router,
                                           prefix=f"{config.PREFIX}",
                                           dependencies=[Depends(authorize)])

                else:
                    cls.app.include_router(sub_module.router,
                                           prefix=f"{config.PREFIX}")

                logger.info(f"子项目加载成功：{dir.name}")

            except Exception:  # pylint: disable=broad-except
                logger.error(f"子路由加载错误：{traceback.format_exc()}")
                pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """生命周期管理
    """

    def on_startup():
        """启动时执行逻辑
        """
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
        """关闭时执行逻辑
        """
        logger.warn("收到关闭信号，FastFlyer 开始执行优雅停止逻辑...")
        # 关闭任务调度器
        logger.info("正在关闭 Apscheduler 定时引擎...")
        background_scheduler.shutdown(wait=True)
        asyncio_scheduler.shutdown(wait=True)
        # 等待一段时间再退出（最小1秒，最大60秒）
        graceful_timeout = max(
            min(int(os.getenv("flyer_graceful_timeout", 1)), 60), 1)
        logger.warn(f"优雅停止逻辑执行完毕，FastFlyer 将在 {graceful_timeout}s 后自动退出...")
        for i in range(0, graceful_timeout):
            time.sleep(1)
            logger.warn(f"退出倒计时：{graceful_timeout - i}s ...")
        logger.warn("FastFlyer 已成功停止服务，感谢您的使用，再见！")

    try:
        on_startup()
        yield
    finally:
        on_shutdown()
