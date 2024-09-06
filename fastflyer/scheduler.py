from os import getenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastkit.utils.scheduler import Scheduler
from fastkit.logging import get_logger
from fastflyer import config

logger = get_logger(logger_name="console", log_path=config.LOG_PATH)

redis_host = getenv("flyer_redis_host")
if redis_host:
    redis_port = int(getenv("flyer_redis_port", "6379"))
    redis_pass = getenv("flyer_redis_pass", "")
    redis_db = int(getenv("flyer_redis_db", "10"))
    redis_nodes = [{
        "host": redis_host,
        "port": redis_port,
        "password": redis_pass,
        "db": redis_db
    }]

else:
    redis_nodes = None

# 线程型后台任务调度
background_scheduler: BackgroundScheduler = Scheduler(
    redis_nodes=redis_nodes,
    name="fastflyer",
    scheduler_type="background",
    logger=logger,
    auto_start=False)

# 协程型后台任务调度
asyncio_scheduler: AsyncIOScheduler = Scheduler(redis_nodes=redis_nodes,
                                                name="fastflyer",
                                                scheduler_type="asyncio",
                                                logger=logger,
                                                auto_start=False)
