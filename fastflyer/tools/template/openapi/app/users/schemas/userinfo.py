# -*- coding: utf-8 -*-
"""
参数定义
"""
from typing import List
from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    """ User信息字段定义
    """
    name: str = Field(example="张三", title="姓名")
    age: str = Field(example="35", title="年龄")
    sex: str = Field(example="男", title="性别")
    father: str = Field(example="", title="父亲")
    mother: str = Field(example="", title="母亲")


class UserCreateRequest(BaseModel):
    """ 创建User：请求参数.
    """
    data: List[UserInfo] = Field(title="返回用户信息列表")
