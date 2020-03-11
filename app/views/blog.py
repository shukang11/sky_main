# -*- coding: utf-8 -*-

from typing import Optional, Any, Dict, List, Tuple
from flask import request, Blueprint
from app.utils import NoResultFound, MultipleResultsFound
from app.utils import UserError, CommonError
from app.utils import response_error, response_succ
from app.utils import (
    get_unix_time_tuple,
    get_date_from_time_tuple,
)
from app.utils import session, parse_params, get_current_user
from app.utils import login_require, pages_info_requires, get_page_info, PageInfo
from app.utils import is_link, get_logger
from app.model import User, Article
import app


api = Blueprint("blog", __name__)

logger = get_logger(__name__)


@api.route("/add/", methods=["POST"])
@login_require
def add_article():
    """ 添加一个订阅 """
    user: User = get_current_user()
    params: Dict[str, Any] = parse_params()
    title: str = params.get("title")
    content: str = params.get("content")
    is_publish: bool = params.get("publish", False)
    if not (title and content):
        return CommonError.get_error(error_code=40000)
    payload: Dict[str, int] = {}
    try:
        blog: Article = Article(user.id, title, content, is_publish=is_publish)
        blog.save(True)
        payload["article_id"] = blog.article_id
    except:
        return CommonError.get_error(error_code=9999)
    else:
        return response_succ(body=payload)


@api.route("/list/", methods=["GET", "POST"])
@login_require
@pages_info_requires
def article_list():
    """ 文章列表 """
    user: User = get_current_user()
    params: Dict[str, Any] = parse_params()
    pageInfo: PageInfo = get_page_info()
    articles: List[Article] = session.query(Article).filter(
        Article.user_id == user.id,
        Article.is_delete == False,
    ).order_by(Article.create_time.desc()).offset(pageInfo.offset).limit(
        pageInfo.limit
    ).all()
    payload: List[Dict[str, Any]] = [{
        'title': a.title,
        'create_time': a.create_time,
    } for a in articles]
    return response_succ(payload)