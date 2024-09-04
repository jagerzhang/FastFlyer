"""内置路由
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastflyer import status
from fastflyer import config

router = APIRouter(tags=["健康检查"])


@router.get("/", include_in_schema=False)
def root():  # NOQA
    """根路径访问自动跳转
    """
    return RedirectResponse(f"{config.PREFIX}/docs", status_code=302)


@router.get(f"{config.PREFIX}/health_check", include_in_schema=True)
@router.get("/health_check", include_in_schema=False)
def health_check():  # NOQA
    """健康检查接口
    """
    return JSONResponse(content={
        "message": "success",
        "code": status.HTTP_200_OK
    })


@router.get("/health_check/async", include_in_schema=False)
async def health_check_async():  # NOQA
    """健康检查接口-异步模式
    """
    return JSONResponse(content={
        "message": "success",
        "code": status.HTTP_200_OK
    })


@router.get(f"{config.PREFIX}/docs", include_in_schema=False)
def docs():  # NOQA
    """ Swagger UI
    """
    return get_swagger_ui_html(
        openapi_url=config.PREFIX + "/openapi.json",
        title=config.API_TITLE + "接口交互文档",
        swagger_js_url=config.PREFIX +
        "/static/swagger-ui-bundle.js?ver=5.1.0",
        swagger_css_url=config.PREFIX + "/static/swagger-ui.css?ver=5.1.0",
        swagger_favicon_url=config.PREFIX + "/static/favicon.ico")


@router.get(f"{config.PREFIX}/redoc", include_in_schema=False)
def redoc():
    """ ReDoc UI
    """
    return get_redoc_html(
        openapi_url=config.PREFIX + "/openapi.json",
        title=config.API_TITLE + "接口交互文档",
        redoc_js_url=config.PREFIX + "/static/redoc.standalone.js",
        redoc_favicon_url=config.PREFIX + "/static/favicon.ico",
        with_google_fonts=False)
