# -*- coding: utf-8 -*-
import fcntl
import os
import socket
import struct
import sys


def get_client_ip(request):
    """get the client IPAddress by request
    """
    try:
        real_ip = request.headers['X-Forwarded-For']
        if len(real_ip.split(',')) > 1:
            client_ip = real_ip.split(",")[0]

        else:
            client_ip = real_ip

    except Exception:  # pylint: disable=broad-except
        client_ip = request.client.host

    return client_ip


def get_host_ip():
    """get the host IPAddress by socket
    """
    host_ip = None
    try:
        socket_fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_fd.connect(("www.qq.com", 80))
        host_ip = socket_fd.getsockname()[0]

    finally:
        socket_fd.close()

    if host_ip:
        return host_ip

    try:
        host_ip = get_ip_by_interface("eth1")

    except OSError:
        try:
            host_ip = get_ip_by_interface("eth0")

        except OSError:
            host_ip = None

    return host_ip


def get_ip_by_interface(ifname):
    """获取指定网卡的IP地址
    """
    ifname = ifname[:15]
    if sys.version_info.major == 3:
        ifname = bytes(ifname, "utf-8")

    socket_fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_addr = socket.inet_ntoa(
        fcntl.ioctl(
            socket_fd.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack("256s", ifname))[20:24])
    return ip_addr


def get_env_list(prefix=None, replace=True):
    """ 获取环境变量
        @ prefix： 指定目标变量的前缀
        @ replace：指定前缀后，键名是否去掉前缀
    """
    env_dict = os.environ

    if prefix:
        env = {}
        for key in env_dict:
            if prefix in key:
                if replace:
                    env[key.replace(prefix, "")] = env_dict[key]
                else:
                    env[key] = env_dict[key]

        return env

    else:
        return dict(env_dict)


def get_log_path(config=None):
    """
    自动获取日志目录
    """
    if hasattr(config, "LOG_DIR"):
        log_path = config.LOG_DIR
    else:
        log_path = f"{os.getcwd()}/logs"

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    return log_path
