# -*- coding: utf-8 -*-
#
# 异常处理相关常量及工具函数等
from traceback import format_exc
from typing import Any
from httptools.parser.errors import HttpParserInvalidMethodError
from fastapi import FastAPI
from fastapi import status as fastapiStatus, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from fastflyer import config, status
from fastkit.logging import get_logger

# 定义返回码基数，最小值为0，默认为 0，和HTTP返回码保持一致
STATUS_CODE_BASE = max(getattr(config, "STATUS_CODE_BASE", 0), 0)

logger = get_logger(logger_name="console", log_path=config.LOG_PATH)


def init_exception(app: FastAPI):
    """初始化异常处理"""

    def get_detail(message: str) -> str:
        return message.strip().split("\n")[-1]

    # pylint: disable=unused-variable
    @app.exception_handler(HttpParserInvalidMethodError)
    async def handle_invalid_http_method_error(request, exc):
        return ErrorResponse(status_code=status.HTTP_400_BAD_REQUEST,
                             message="非法的请求方法",
                             detail=str(exc))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: Exception):
        """请求参数异常"""
        return ErrorResponse(status.HTTP_400_BAD_REQUEST,
                             message="请求参数校验不通过",
                             detail=str(exc))

    @app.exception_handler(ValidationError)
    async def resp_validation_exception_handler(request, exc: Exception):
        """响应值参数校验异常"""
        return ErrorResponse(status.HTTP_403_FORBIDDEN,
                             message="响应参数校验不通过",
                             detail=str(exc))

    @app.exception_handler(BaseException)
    async def base_exception_handler(request, exc: BaseException):
        """捕获自定义异常"""
        # 把异常的详细信息打印到控制台，也可以在此实现将日志写入到对应的文件系统等
        logger.warning(format_exc())
        return ErrorResponse(exc.code, message=exc.message, detail=exc.detail)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        """捕获FastAPI异常"""
        logger.warning(format_exc())
        return ErrorResponse(exc.status_code,
                             message=str(exc.detail),
                             detail=exc.detail)

    @app.exception_handler(Exception)
    async def allexception_handler(request, exc: Exception):
        """捕获所有其他的异常
        """
        message = format_exc()
        logger.warning(message)
        return ErrorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR,
                             message="内部异常",
                             detail=get_detail(message))

    @app.exception_handler(KeyError)
    async def keyerror_handler(request, exc: KeyError):
        """捕获所有其他的异常"""
        message = format_exc()
        logger.warning(message)
        return ErrorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR,
                             message="内部异常",
                             detail=get_detail(message))

    @app.exception_handler(ValueError)
    async def valueerror_handler(request, exc: ValueError):
        """捕获所有其他的异常"""
        message = format_exc()
        logger.warning(message)
        return ErrorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR,
                             message="内部异常",
                             detail=get_detail(message))

    # pylint: disable=unused-variable


# 状态码对应的异常信息(默认)
messages = {
    # 4XX
    status.HTTP_400_BAD_REQUEST: "请求参数校验不通过",
    status.HTTP_401_UNAUTHORIZED: "权限校验不通过",
    status.HTTP_403_FORBIDDEN: "响应参数校验不通过",
    status.HTTP_404_NOT_FOUND: "请求的资源不存在",
    # 5XX
    status.HTTP_500_INTERNAL_SERVER_ERROR: "服务器内部错误",
    status.HTTP_504_GATEWAY_TIMEOUT: "请求上游服务时超时",
}


class BaseException(HTTPException):
    """自定义异常基类
    程序内部抛出的异常应该给予该基类
    异常都使用这个类型或者其子类进行抛出，会被统一进行处理和响应。
    对于嵌套的异常处理，如果捕获到这个类型的，则直接raise即可，其他的异常则可以进行进一步的处理。
    """

    def __init__(self,
                 code: int,
                 message: str = None,
                 detail: Any = None) -> None:
        """
        :param code 必须是在在status中定义好的值
        :param message 异常信息，通常可以展示给前端用户看
        :param detail 详细异常信息，通常是用于开发排查问题
        """
        self.code = code
        self.message = message if message else messages[code]
        status_code = code if code < 600 else fastapiStatus.HTTP_500_INTERNAL_SERVER_ERROR
        super().__init__(status_code, detail)

    def __str__(self) -> str:
        return f"code={self.code} message={self.message}\n detail={self.detail}"


class InternalException(BaseException):
    """内部错误异常
    异常时通常使用该类型进行raise
    """
    pass


class ErrorResponse(JSONResponse):
    """接口异常响应类型
    通常只需要在中间件捕获异常的时候使用。
    异常时可以指定一个状态，这个状态码应该尽量重用http标准的状态码，
    对于超过范围的值，可以定义到600到999的范围，大于等于600的时候，
    在响应时会自动重置为500.
    响应给前端的异常信息结构(假设SYSTEM_CODE_BASE的值为1000)：
    Example1:
    {
        "code": 1401,
        "message": "这是自定义错误信息"
    }
    这时http响应的状态码应该时401
    Example2:
    {
        "code": 1602,
        "message": "这是自定义错误信息"
    }
    这时http响应的状态码应该时500（大于等于600时自动重置为500）

    其中：
    code值是完整的异常状态码，message是异常描述信息。
    """
    """
        :param code 响应状态码，正常取值0-999，若该值与1000的余数大于等于600，则http code会自动重置为500。若该值大于等于1000，则该值可能来自上游接口
        :param message 异常信息，通常是用于展示给用户。如果该值为空，则会默认为code值对应的异常信息
        :param detail 详细的异常信息，通常用于开发者排除定位问题使用
        """

    def __init__(self,
                 code: int,
                 message: str = None,
                 detail: Any = None,
                 content: dict = None,
                 status_code: int = 200) -> None:
        """通用JSON响应类

        Args:
            code (int): Body 响应码，200为正常，其他为异常
            message (str, optional): 异常信息. Defaults to None.
            detail (Any, optional): 详细的异常信息. Defaults to None.
            content (dict, optional): 正常请求下的JSON响应内容. Defaults to None.
            status_code (int, optional): HTTP响应码，默认一直为200. Defaults to 200.
        """
        base_content = {}
        content = content or {}
        base_content["code"] = code
        base_content["message"] = message if message else messages.get(
            code, "")
        base_content["detail"] = detail if detail else ""

        base_content.update(content)

        if code == fastapiStatus.HTTP_200_OK:
            super().__init__(status_code=status_code, content=base_content)
            return

        # http的状态码大于600会报错，超过600响应为内部错误
        status_code = status_code if status_code < 600 else status.HTTP_500_INTERNAL_SERVER_ERROR
        # 消息返回码叠加一下基数
        base_content["code"] = STATUS_CODE_BASE + code
        super().__init__(status_code=status_code, content=base_content)


if __name__ == "__main__":
    resp = ErrorResponse(status.HTTP_403_FORBIDDEN, message="接口请求参数错误")
    logger.info(resp.body)
