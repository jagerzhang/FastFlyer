from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastkit.utils.scheduler import get_scheduler
from fastkit.logging import get_logger
from fastflyer import config

logger = get_logger(logger_name="console", log_path=config.LOG_PATH)

# 线程型后台任务调度
background_scheduler: BackgroundScheduler = get_scheduler(
    name="fastflyer",
    scheduler_type="background",
    logger=logger,
    auto_start=False)

# 协程型后台任务调度
asyncio_scheduler: AsyncIOScheduler = get_scheduler(name="fastflyer",
                                                    scheduler_type="asyncio",
                                                    logger=logger,
                                                    auto_start=False)
