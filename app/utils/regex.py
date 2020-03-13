# -*- coding: utf-8 -*-

import re
from typing import Optional

def is_emoji(content: str) -> bool:
    """ judge str is emoji

    Args: str type 

    Return : Bool type , return True if is Emoji , else False
    """
    if not content:
        return False
    if u"\U0001F600" <= content and content <= u"\U0001F64F":
        return True
    elif u"\U0001F300" <= content and content <= u"\U0001F5FF":
        return True
    elif u"\U0001F680" <= content and content <= u"\U0001F6FF":
        return True
    elif u"\U0001F1E0" <= content and content <= u"\U0001F1FF":
        return True
    else:
        return False


def is_link(url: Optional[str]) -> bool:
    """  验证是否是一个链接
    Args:
        url: 需要验证的字符
    Return: 如果是合法的链接，返回 True ，否则返回 False
    """
    regex = r'(https?)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]'
    result: Optional[re.Match] = re.match(regex, url)
    return False if not result else True

def is_phone(content: str) -> bool:
    """  验证是否是一个手机号
    Args:
        url: 需要验证的号码
    Return: 如果是合法的，返回 True ，否则返回 False
    """
    regex = r'1[3|4|5|7|8][0-9]{9}'
    result: Optional[re.Match] = re.match(regex, content)
    return False if not result else True


def is_email(content: str) -> bool:
    """  验证是否是一个邮箱
    Args:
        url: 需要验证的邮箱
    Return: 如果是合法的，返回 True ，否则返回 False
    """
    regex = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
    result: Optional[re.Match] = re.match(regex, content)
    return False if not result else True