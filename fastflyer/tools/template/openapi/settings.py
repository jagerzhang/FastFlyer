from os import getenv
from fastflyer.settings import BaseConfig


class CustomConfig(BaseConfig):
    """
    自定义配置

    Args:
        BaseConfig (_type_): 框架默认配置
    """

    # 定义项目标题
    API_TITLE = "Flyer Demo"

    # 定义接口path
    PREFIX = getenv("flyer_base_url", "/flyer")
    DESCRIPTION = "<br>".join(
        (
            "**中文名称**：FastFlyer 初始项目",
            "**功能说明**：这是由 FastFlyer 框架创建的初始项目，你可以继续开发。",
            "**框架源码**：[FastFlyer](https://github.com/jagerzhang/FastFlyer)",
            f"**接口文档**：[ReDoc]({PREFIX}/redoc)",
            f"**快速上手**：[SwaggerUI]({PREFIX}/docs)",
            f"**最新发布**：{BaseConfig.RELEASE_DATE}",
        )
    )

    # 其他变量请参考BaseConfig内容
