# -*- coding: utf-8 -*-
"""
聚合路由
"""
# -*- coding: utf-8 -*-
from fastflyer import APIRouter
from .userinfo import router as user_router
from .relationship import router as relate_router

router = APIRouter()
router.include_router(user_router, tags=["用户管理"], prefix="/users")
router.include_router(relate_router, tags=["用户管理"], prefix="/users")
