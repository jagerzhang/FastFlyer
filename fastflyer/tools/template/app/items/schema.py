# -*- coding: utf-8 -*-
"""
参数定义
"""
from pydantic import BaseModel, Field


class DemoRequest(BaseModel):
    """ Demo演示：请求参数.
    """
    msgContent: str = Field(example="Flyer", title="Flyer演示项目")
