# -*- coding: utf-8 -*-
"""
任务管理
"""
from fastapi import APIRouter
from fastflyer import status, background_scheduler, config
from fastflyer.schemas import DataResponse, BaseResponse
from fastflyer.middleware import MiddleWare

router = APIRouter(tags=["任务管理"], prefix=config.PREFIX, route_class=MiddleWare)


# pylint: disable=invalid-name
@router.get("/tasks", response_model=DataResponse, summary="任务查询接口")
def get_jobs():
    """查询所有任务
    """
    jobs = background_scheduler.get_jobs()
    job_list = []
    for job in jobs:
        job_info = {
            "id": job.id,
            "name": job.name,
            "nextRunTime": job.next_run_time,
            "trigger": job.trigger.__class__.__name__,
            "args": job.args,
            "kwargs": job.kwargs,
            "misfireGraceTime": job.misfire_grace_time,
            "maxInstances": job.max_instances
        }
        job_list.append(job_info)
    return {"data": job_list}


@router.get("/tasks/{taskId}", response_model=DataResponse, summary="查询指定任务")
def get_job(taskId: str):
    """
    查询指定任务
    """
    job = background_scheduler.get_job(taskId)
    if job:
        job_info = {
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time,
            "trigger": job.trigger.__class__.__name__,
            "args": job.args,
            "kwargs": job.kwargs,
            "misfire_grace_time": job.misfire_grace_time,
            "max_instances": job.max_instances
        }
        return {"data": job_info}
    else:
        return {
            "code": status.HTTP_404_NOT_FOUND,
            "message": f"Job {taskId} not found."
        }


@router.post("/tasks/{taskId}", response_model=BaseResponse, summary="启动指定任务")
def start_job(taskId: str):
    """
    启动指定任务
    """
    job = background_scheduler.get_job(taskId)
    if job:
        if not job.next_run_time:  # 检查任务是否已停止
            background_scheduler.resume_job(taskId)
            return {"message": f"Job {taskId} has been started."}
        else:
            return {"message": f"Job {taskId} is already running."}
    else:
        return {
            "code": status.HTTP_404_NOT_FOUND,
            "message": f"Job {taskId} not found."
        }


@router.delete("/tasks/{taskId}",
               response_model=BaseResponse,
               summary="停止任务接口")
def stop_job(taskId: str):
    """
    停止指定任务
    """
    job = background_scheduler.get_job(taskId)
    if job:
        background_scheduler.remove_job(taskId)
        return {
            "code": status.HTTP_200_OK,
            "message": f"Job {taskId} has been stopped."
        }
    else:
        return {
            "code": status.HTTP_404_NOT_FOUND,
            "message": f"Job {taskId} not found."
        }


@router.delete("/tasks", response_model=DataResponse, summary="停止所有任务")
def stop_jobs():
    """
    停止所有任务
    """
    jobs = background_scheduler.get_jobs()
    stopped_jobs = []
    for job in jobs:
        # 框架本身任务不被停止
        if job.id == "polaris_heartbeat" or job.id.startswith("sync_config_"):
            continue
        background_scheduler.remove_job(job.id)
        stopped_jobs.append({"id": job.id, "name": job.name})

    return {"data": stopped_jobs}


# pylint: disable=invalid-name
