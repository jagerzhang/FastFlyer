# -*- coding: utf-8 -*-
"""
参数验证模块
"""
from typing import Optional, Union
from pydantic import BaseModel, Field
from fastflyer import status


class BaseResponse(BaseModel):
    """ Demo演示：响应参数.
    """
    code: int = Field(
        default=status.HTTP_200_OK,
        example=status.HTTP_200_OK,  # NOQA
        title="返回码",
        description="返回码，0表示成功，其他表示失败")
    message: str = Field(default="", example="", title="异常或提示信息")
    detail: str = Field(default="", example="", title="详细的异常或提示信息")


class PageInfo(BaseModel):
    """
    分页数据定义

    Args:
        BaseResponse (_type_): _description_
    """
    total: int = Field(
        default=0,
        example=0,  # NOQA
        title="返回数据总条数")
    offset: int = Field(
        default=1,
        example=1,  # NOQA
        title="返回数据的分页位置，用于按批次连续拉取")
    size: int = Field(
        default=50,
        example=50,  # NOQA
        title="返回数据的分页大小，默认为50")


class PageDataResponse(BaseResponse):
    """
    带分页数据响应

    Args:
        BaseResponse (_type_): _description_
    """
    pageInfo: Optional[PageInfo] = Field(default={}, title="返回数据的页面信息")
    data: Union[list, dict] = Field(default=[], example=[], title="接口返回的详细数据")


class DataResponse(BaseResponse):
    """
    数据通用响应

    Args:
        BaseResponse (_type_): _description_
    """
    data: Union[list, dict] = Field(default=[], example=[], title="接口返回的详细数据")
