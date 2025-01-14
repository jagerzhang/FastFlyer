"""管理工具
"""

import os
import sys
import glob
import shutil
import argparse
from datetime import datetime
import pkg_resources
from fastkit.logging import get_logger
from fastflyer import threadpool

logger = get_logger(logger_name="console")
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_DEFAULT = "\033[39m"
COLOR_RESET = "\033[0m"


def colored_cover(message, color=COLOR_YELLOW):
    return f"{color}{message}{COLOR_RESET}"


def main():
    try:
        parser = argparse.ArgumentParser(description="FastFlyer 框架开发辅助工具")
        subparsers = parser.add_subparsers(dest="command")

        # 修改为 create 命令
        create_parser = subparsers.add_parser("create", help="创建应用代码")
        create_parser.add_argument("type", choices=["openapi"], help="选择创建类型")
        create_parser.add_argument("--name", help="指定API名称")
        create_parser.add_argument("--prefix", help="指定API接口路径前缀，默认为 /flyer")
        create_parser.add_argument("-f", "--force", action="store_true", help="强制覆盖已存在文件")

        # 修改为 show 命令
        show_parser = subparsers.add_parser("show", help="显示相关信息")
        show_subparsers = show_parser.add_subparsers(dest="show_command")

        show_subparsers.add_parser("openapi", help="快速启动 OpenAPI 示例项目")

        args = parser.parse_args()

        if args.command == "create":
            if args.type in ["openapi"]:
                if os.path.exists(".init_lock") and not args.force:
                    logger.warn("项目已经被初始化过，请勿重复初始化")
                else:
                    template_dir = pkg_resources.resource_filename(__name__, f"template/{args.type}")
                    copy_files(template_dir, ".", args.force)

                    # 读取 --name 和 --prefix 参数
                    name = args.name if args.name else "Flyer Demo"
                    prefix = args.prefix if args.prefix else "/flyer"

                    # 替换 settings.py 文件中的 API_TITLE 和 PREFIX
                    settings_file = f"{template_dir}/settings.py"
                    with open(settings_file, "r") as f:
                        filedata = f.read()
                    filedata = filedata.replace('API_TITLE = "Flyer Demo"', f'API_TITLE = "{name}"')
                    filedata = filedata.replace(
                        'PREFIX = getenv("flyer_base_url", "/flyer")', f'PREFIX = getenv("flyer_base_url", "{prefix}")'
                    )
                    with open(settings_file, "w") as f:
                        f.write(filedata)

                    if os.path.exists(".init_lock"):
                        os.remove(".init_lock")
                    with open(".init_lock", "w") as lock_file:
                        lock_file.write(str(datetime.now()))
                    logger.info(
                        f"初始化完成，你可以执行 ls 命令查看目录内容或执行{colored_cover('./dev_ctrl.sh')}快速构建开发环境"
                    )

        elif args.command == "show":
            if args.show_command == "openapi":
                logger.info("尝试读取相关环境变量...")
                for key, value in os.environ.items():
                    if not key.startswith("flyer_"):
                        continue
                    logger.info(f"{key}={value}")

                from fastflyer.tools.template.openapi.main import main_cmd
                from fastflyer.utils import get_host_ip

                port = os.getenv("flyer_port", "8080")
                prefix = os.getenv("flyer_base_url", "/flyer")
                url = f"http://{get_host_ip()}:{port}{prefix}"
                logger.info("欢迎启动 FastFlyer OpenAPI 体验项目，现在可以通过浏览器访问以下项目页面：")
                logger.info(f"SwaggerUI 文档：{colored_cover(f'{url}/docs')}")
                logger.info(f"ReDoc 接口文档：{colored_cover(f'{url}/redoc')}")
                main_cmd()

            else:
                parser.print_help()

        else:
            # 如果没有指定命令，则输出帮助信息
            parser.print_help()

    finally:
        # 在所有情况下都调用 shutdown
        threadpool.shutdown(wait=False, show_log=False)


def copy_files(source_dir, dest_dir, force=False):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    copied_files = []  # 用于跟踪已经拷贝过的文件路径

    for root, dirs, files in os.walk(source_dir):
        for dir in dirs:
            if dir == "__pycache__":
                continue
            src_dir = os.path.join(root, dir)
            dest_subdir = os.path.join(dest_dir, os.path.relpath(src_dir, source_dir))

            is_copied = False
            for copied_dir in copied_files:
                if dest_subdir.startswith(copied_dir):
                    is_copied = True
                    break

            if is_copied:
                continue

            if not force and os.path.exists(dest_subdir):
                logger.warn(f"目录 {dest_subdir} 已存在. 请添加 --force 参数执行强制覆盖")
            else:
                if sys.version_info >= (3, 8):
                    shutil.copytree(src_dir, dest_subdir, dirs_exist_ok=True)
                else:
                    shutil.copytree(src_dir, dest_subdir)
                copied_files.append(dest_subdir)  # 添加已拷贝的目录路径到列表

        for file in files:
            if file.endswith((".pyc", ".log", ".lock")):
                continue  # 排除后缀为 .pyc 和 .log 的文件
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_dir, os.path.relpath(src_file, source_dir))

            is_copied = False
            for copied_dir in copied_files:
                if dest_file.startswith(copied_dir):
                    is_copied = True
                    break

            if is_copied:
                continue

            if not force and os.path.exists(dest_file):
                logger.warn(f"文件 {dest_file} 已存在. 请添加 --force 参数执行强制覆盖")
            else:
                shutil.copy2(src_file, dest_file)

    # 删除当前目录下以 .log 结尾的文件
    for file in glob.glob("*.log"):
        os.remove(file)


if __name__ == "__main__":
    main()
