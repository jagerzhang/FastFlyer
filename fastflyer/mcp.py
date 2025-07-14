import re
from os import getenv
from fastflyer import FlyerAPI, logger
from fastapi_mcp import FastApiMCP


def config_mcp(app: FlyerAPI, mount_path="/mcp", mount_kwargs: dict = None, **kwargs):
    """配置 MCP

    Args:
        app (FlyerAPI): FlyerAPI
        mount_kwargs (dict, optional): mount拓展参数. Defaults to None.
        **kwargs: 其他 FastApiMCP 参数
    """

    # 启用 MCP SSE 服务
    mcp_enabled = int(getenv("flyer_mcp_enabled", 0))
    # MCP 暴露指定标签的接口
    mcp_include_tags = getenv("flyer_mcp_include_tags")
    if mcp_include_tags:
        mcp_include_tags = re.split(r"\s*[,|;]\s*", mcp_include_tags.strip())
    # MCP 屏蔽指定标签的接口
    mcp_exclude_tags = getenv("flyer_mcp_exclude_tags")
    if mcp_exclude_tags:
        mcp_exclude_tags = re.split(r"\s*[,|;]\s*", mcp_exclude_tags.strip())
    # MCP 暴露指定接口
    mcp_include_operations = getenv("flyer_mcp_include_operations")
    if mcp_include_operations:
        mcp_include_operations = re.split(r"\s*[,|;]\s*", mcp_include_operations.strip())
    # MCP 屏蔽指定接口
    mcp_exclude_operations = getenv("flyer_mcp_exclude_operations")
    if mcp_exclude_operations:
        mcp_exclude_operations = re.split(r"\s*[,|;]\s*", mcp_exclude_operations.strip())

    if mcp_enabled:
        logger.info(f"已启用 MCP 服务，挂载路径为 {mount_path}")
        mount_kwargs = mount_kwargs or {}
        mcp = FastApiMCP(
            app,
            include_tags=mcp_include_tags,
            exclude_tags=mcp_exclude_tags,
            include_operations=mcp_include_operations,
            exclude_operations=mcp_exclude_operations,
            **kwargs,
        )
        mcp.mount(mount_path=mount_path, **mount_kwargs)
