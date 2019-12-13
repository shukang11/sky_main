# -*- coding: utf-8 -*-

from typing import Optional, Callable, AnyStr, Union, Tuple, Dict

from functools import wraps
from flask import request, Request, session
from app.utils import CommonError, UserError
from app.utils import redisClient
from app.model import User

def login_option(func: Callable):
    """  处理请求中的用户信息，并封装到 `g` 中
    """
    @wraps(func)
    def decorator_view(*args, **kwargs):
        user_or_error: Optional[any] = get_user_from_request(request, False)
        if user_or_error:
            g.c_user = user_or_error
        return func(*args, **kwargs)
    return decorator_view

def login_require(func: Callable):
    """
    检测登录权限
    在执行 func 之前，会检查权限
    :param func:  被执行的 router_func
    """
    @wraps(func)
    def decorator_view(*args, **kwargs):
        userOrError: any = get_user_from_request(request, True)
        if not userOrError:
            return UserError.get_error(40204)
        if isinstance(userOrError, User):
            g.current_user = userOrError
        else:
            return userOrError
        return func(*args, **kwargs)
    return decorator_view

def get_user_from_request(request: Request, is_force: bool) -> Union[Optional[User], Tuple[str, int, Dict[str, str]]]:
    """  尝试从请求中获得用户
    Args:
        request: 一个请求的实例
        is_force: 是否是强制需要用户信息， 如果是强制的，在没有获得用户的时候会返回一个错误报文
    Return: 获得的用户实例，如果根据信息无法获得用户实例，则返回 None
    """
    params = request.values or request.get_json() or {}
    alise: AnyStr = 'token'
    token: Optional[AnyStr] = params.get(alise)
    if not token:
        token = session.get(alise) or request.cookies.get(alise)
    if not token and is_force:
        return CommonError.get_error(40000)
    if not token: return None
    user_id: int = redisClient.get(token)
    user: User = User.get_user(uid=user_id)
    return user
    