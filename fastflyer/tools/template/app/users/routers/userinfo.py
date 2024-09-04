# -*- coding: utf-8 -*-
"""
用户信息路由
"""
from fastflyer import status
from fastflyer.schemas import DataResponse
from fastflyer import APIRouter
from users.schemas.userinfo import UserCreateRequest

router = APIRouter()


@router.post("/info", response_model=DataResponse, summary="用户录入接口")
async def create_user(params: UserCreateRequest):
    """
    演示接口：批量录入用户信息
    ---
    - 附加说明2: 这个位置可以加入更多说明列表。
    """
    result = {"code": status.HTTP_200_OK, "message": "", "data": params.data}
    return result
