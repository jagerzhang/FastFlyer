import os
import sys
import glob
import shutil
import argparse
from datetime import datetime
import pkg_resources
from fastkit.logging import get_logger

logger = get_logger(logger_name="console", log_path="/var/log")
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_DEFAULT = "\033[39m"
COLOR_RESET = "\033[0m"


def colored_cover(message, color=COLOR_YELLOW):
    return f"{color}{message}{COLOR_RESET}"


def main():
    parser = argparse.ArgumentParser(description="FastFlyer 框架开发辅助工具")
    subparsers = parser.add_subparsers(dest="command")
    create_app_parser = subparsers.add_parser("init_app", help="初始化应用代码")
    subparsers.add_parser("show_demo", help="快速启动内置示例项目")
    create_app_parser.add_argument("-f",
                                   "--force",
                                   action="store_true",
                                   help="强制覆盖已存在文件")

    args = parser.parse_args()

    if args.command == "init_app":
        # 检查是否已经初始化过，或者使用 -f 选项来强制重新创建
        if os.path.exists(".init_lock") and not args.force:
            logger.warn("项目已经被初始化过，请勿重复初始化")
        else:
            # 获取 SDK 包内 demo 目录的路径
            demo_dir = pkg_resources.resource_filename(__name__, "template")
            # 拷贝 demo 目录下的文件到当前目录
            copy_files(demo_dir, ".", args.force)
            # 如果已经初始化过，删除 .init_lock 文件
            if os.path.exists(".init_lock"):
                os.remove(".init_lock")
            # 创建并写入 .init_lock 文件
            with open(".init_lock", "w") as lock_file:
                lock_file.write(str(datetime.now()))
            logger.info(
                f"初始化完成，你可以执行 ls 命令查看目录内容或执行{colored_cover('./dev_ctrl.sh')}快速构建开发环境"
            )

    elif args.command == "show_demo":
        logger.info("尝试读取相关环境变量...")
        for key, value in os.environ.items():
            if not key.startswith("flyer_"):
                continue
            logger.info(f"{key}={value}")

        from fastflyer.tools.template.main import main_cmd
        from fastflyer.utils import get_host_ip
        port = os.getenv("flyer_port", 8080)
        prefix = os.getenv("flyer_base_url", "/flyer")
        url = f"http://{get_host_ip()}:{port}{prefix}"
        logger.info("欢迎启动体验项目，现在可以通过浏览器访问以下项目页面：")
        logger.info(f"SwaggerUI 文档：{colored_cover(f'{url}/docs')}")
        logger.info(f"ReDoc 接口文档：{colored_cover(f'{url}/redoc')}")
        main_cmd()

    else:
        # 如果没有指定命令，则输出帮助信息
        parser.print_help()


def copy_files(source_dir, dest_dir, force=False):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    copied_files = []  # 用于跟踪已经拷贝过的文件路径

    for root, dirs, files in os.walk(source_dir):
        for dir in dirs:
            if dir == "__pycache__":
                continue
            src_dir = os.path.join(root, dir)
            dest_subdir = os.path.join(dest_dir,
                                       os.path.relpath(src_dir, source_dir))

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
            dest_file = os.path.join(dest_dir,
                                     os.path.relpath(src_file, source_dir))

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
