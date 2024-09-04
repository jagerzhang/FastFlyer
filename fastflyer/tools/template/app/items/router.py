# -*- coding: utf-8 -*-
"""
路由文件
"""
from fastflyer import status
from fastflyer.schemas import DataResponse
from fastflyer import APIRouter

router = APIRouter(tags=["项目管理"])


@router.get("/items/{id}", response_model=DataResponse, summary="项目查询接口")
async def get_item(id: int):
    """
    演示接口：项目信息查询
    ---
    - 附加说明2: 这个位置可以加入更多说明列表。
    """
    result = {"code": status.HTTP_200_OK, "data": {"itemId": id}}
    return result
