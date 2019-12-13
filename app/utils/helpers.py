# -*- coding: utf-8 -*-

from typing import TypeVar, Dict, AnyStr, Any, Optional

from app.model import User
"""
Helper functions
"""

def parse_params(request: TypeVar) -> Dict[AnyStr, Any]:
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
        return getattr(g, 'current_user', None)
    except expression as e:
        return None
