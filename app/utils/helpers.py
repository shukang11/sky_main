# -*- coding: utf-8 -*-

from typing import TypeVar, Dict, AnyStr, Any, Optional
import logging
import sys
from os import makedirs
from os.path import dirname, exists
from app.model import User

"""
Helper functions
"""


def parse_params(request: Any) -> Dict[AnyStr, Any]:
    """  从一个Request实例中解析params参数
    Args:
        request: flask.request 实例对象
    Return: 一个解析过的字典对象，如果没有解析出，则返回一个空的字典对象
    """
    params = request.values or request.get_json() or {}
    return dict(params)


def get_current_user() -> Optional[User]:
    """  尝试从当前服务实例中获得附加的用户实例
    Args:
        g: flask 的 g 对象
    Return:
        如果其中附加了用户实例，则返回，如果没有就返回None
    """
    try:
        from flask import g

        return getattr(g, "current_user", None)
    except Exception as e:
        return None

class PageInfo:
    page: int = 0
    limit: int = 11
    offset: int = 0

    def __init__(self, page: int, limit: int):
        self.pages = page
        self.limit = limit
        self.offset = page * limit

def get_page_info() -> Optional[PageInfo]:
    """  尝试从当前服务实例中获得附加的页面实例
    Args:
        g: flask 的 g 对象
    Return:
        如果其中附加了页面实例，则返回，如果没有就返回None
    """
    try:
        from flask import g

        return getattr(g, "pageinfo", None)
    except Exception as e:
        return None


loggers: Dict[str, Any] = {}

LOG_ENABLE = True  # 是否开启日志
LOG_LEVEL = "DEBUG"  # 日志输出等级
LOG_FORMAT = "%(levelname)s - %(asctime)s - process: %(process)d - %(filename)s - %(name)s - %(lineno)d - %(module)s - %(message)s"  # 每条日志输出格式


def get_logger(name: Optional[str] = None):
    """  获得一个logger 实例，用来打印日志
    Args: 
        name: logger的名称
    Return:
        返回一个logger实例
    """
    global loggers

    if not name:
        name = __name__

    if loggers.get(name):
        return loggers.get(name)

    logger = logging.getLogger(name=name)
    logger.setLevel(LOG_LEVEL)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(LOG_LEVEL)
    formatter = logging.Formatter(LOG_FORMAT)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    loggers[name] = logger

    return logger
