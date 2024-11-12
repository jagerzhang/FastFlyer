# -*- coding: utf-8 -*-
"""
用户关系路由
"""
from fastflyer import status
from fastflyer.schemas import DataResponse
from fastflyer import APIRouter

router = APIRouter()


@router.get("/relationship/{username}",
            response_model=DataResponse,
            summary="关系查询接口")
async def relationship(username: str):
    """
    演示接口：查询用户关系
    ---
    - 附加说明1: 仅用于演示，请勿对号入座；
    - 附加说明2：这个位置可以加入更多说明列表。
    """
    data = {"father": f"{username}'s father", "mother": f"{username}'s mother"}
    result = {"code": status.HTTP_200_OK, "msg": "", "data": data}
    return result
