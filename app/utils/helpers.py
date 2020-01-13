# -*- coding: utf-8 -*-

from typing import Dict, AnyStr, Any, Optional, Type
import logging
import sys
import os
from config import configInfo, Config

"""
Helper functions
"""


def parse_params(request: Any) -> Dict[str, Any]:
    """  从一个Request实例中解析params参数
    Args:
        request: flask.request 实例对象
    Return: 一个解析过的字典对象，如果没有解析出，则返回一个空的字典对象
    """
    params = request.values or request.get_json() or {}
    return dict(params)


def get_current_user() -> Any:
    """  尝试从当前服务实例中获得附加的用户实例
    g: flask 的 g 对象
    Return:
        如果其中附加了用户实例，则返回，如果没有就返回None
    """
    from flask import g

    return getattr(g, "current_user", None)


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
    g: flask 的 g 对象
    Return:
        如果其中附加了页面实例，则返回，如果没有就返回None
    """
    from flask import g

    return getattr(g, "pageinfo", None)


loggers: Dict[str, logging.Logger] = {}


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """  获得一个logger 实例，用来打印日志
    Args: 
        name: logger的名称
    Return:
        返回一个logger实例
    """
    global loggers

    if not name:
        name = __name__

    env: str = os.environ.get("FLASK_ENV", "default")
    config: Any = configInfo.get(env)
    has = loggers.get(name)
    if has:
        return has

    logger = logging.getLogger(name=name)
    logger.setLevel(config.LOG_LEVEL)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(config.LOG_LEVEL)
    formatter = logging.Formatter(config.LOGGING_FORMATTER)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    loggers[name] = logger

    return logger
