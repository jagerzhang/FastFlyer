from os import getenv, environ
from fastkit.logging import get_logger  # noqa

log_path = getenv("flyer_log_path", "/var/log")
logger = get_logger(logger_name="console",
                    file_log_level=getenv("flyer_file_log_level"),
                    console_log_level=getenv("flyer_console_log_level"),
                    log_path=log_path)

logger.info("已加载环境变量如下：")
for k, v in environ.items():
    if len(v.split("\n")) > int(getenv("flyer_max_wrap_line") or 10):
        v = v.replace("\n", "\\n")
    logger.info(f"{k}: {v}")
