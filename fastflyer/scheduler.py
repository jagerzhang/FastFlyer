"""任务调度
"""
from os import getenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastkit.executor import Scheduler, ThreadPoolExecutor
from fastkit.logging import get_logger
from fastflyer import config

logger = get_logger(logger_name="console", log_path=config.LOG_PATH)

redis_host = getenv("flyer_redis_host")
REDIS_CONFIG = None
if redis_host:
    redis_port = int(getenv("flyer_redis_port", "6379"))
    redis_pass = getenv("flyer_redis_pass", "")
    redis_db = int(getenv("flyer_redis_db", "10"))
    REDIS_CONFIG = {
        "host": redis_host,
        "port": redis_port,
        "passwd": redis_pass,
        "database": redis_db
    }

max_threads = int(getenv("flyer_threads", "5"))
# 线程型后台任务调度
background_scheduler: BackgroundScheduler = Scheduler(
    redis_config=REDIS_CONFIG,
    name="fastflyer",
    scheduler_type="background",
    logger=logger,
    auto_start=False,
    executor_type="threadpool",
    pool_size=max_threads)

# 协程型后台任务调度
asyncio_scheduler: AsyncIOScheduler = Scheduler(redis_config=REDIS_CONFIG,
                                                name="fastflyer",
                                                scheduler_type="asyncio",
                                                logger=logger,
                                                auto_start=False,
                                                executor_type="threadpool",
                                                pool_size=max_threads)

# 线程池后台任务
threadpool = ThreadPoolExecutor(redis_config=REDIS_CONFIG)
