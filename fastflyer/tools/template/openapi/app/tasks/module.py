"""示例任务
"""
from fastflyer import logger, background_scheduler, threadpool


# 定时任务示例：每5秒执行一次
@background_scheduler.scheduled_job('interval', seconds=5, single_job=True)
def hello_world():
    logger.info("hello world by background-scheduler every 5 senconds!")


# 后台线程执行示例
# @threadpool.submit()  # 支持装饰器添加方式
def hello_world_thread():
    # 直到线程池停止才结束循环
    while not threadpool.is_stopped():
        logger.warning("hello world by threadpool every 5 senconds!")
        threadpool.sleep(5)
