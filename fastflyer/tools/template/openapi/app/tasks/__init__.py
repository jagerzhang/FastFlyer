"""后台任务示例
"""
from fastflyer import threadpool
from .module import hello_world_thread

# 显式添加后台线程任务方式（也支持装饰器添加方式）
threadpool.submit_task(hello_world_thread)
