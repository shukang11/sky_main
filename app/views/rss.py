# -*- coding: utf-8 -*-

from typing import Optional, AnyStr, Dict, List
from flask import request, Blueprint
from sqlalchemy import and_
from app.utils import UserError, CommonError
from app.utils import response_error, response_succ
from app.utils import get_random_num, get_unix_time_tuple, getmd5
from app.utils import session, parse_params, get_current_user
from app.utils import login_require, pages_info_requires, get_page_info, PageInfo
from app.utils import is_link, get_logger
from app.task import rss as RssTask
from app.model import User, RssContentModel, RssModel, RssReadRecordModel, RssUserModel
import app

api = Blueprint("rss", __name__)
app.fetch_route(api, "/rss")

logger = get_logger(__name__)


@api.route("/add", methods=["POST"])
@login_require
def add_rss_source():
    """ 添加一个订阅源
    try add a url to rss list
    """
    params = parse_params(request)
    user: User = get_current_user()
    source = params.get("source")
    if not source:
        return CommonError.get_error(40000)
    if not is_link(source):
        return CommonError.error_toast("wrong link")

    rss_id: Optional[int] = None
    # 检查是否存在rss
    exists_rss: RssModel = RssModel.query.filter(RssModel.rss_link == source).first()
    if exists_rss:
        rss_id = exists_rss.rss_id
    else:
        rss = RssModel(source, add_time=get_unix_time_tuple())
        session.add(rss)
        session.flush()
        rss_id = rss.rss_id
    # 是否存在关系
    exsits_relationship: RssUserModel = RssUserModel.query.filter(
        RssUserModel.user_id == user.id, RssUserModel.rss_id == rss_id
    ).first()
    payload: Dict[AnyStr, any] = {}
    if exsits_relationship:
        payload["rss_id"] = rss_id
    else:
        rss_user = RssUserModel(user.id, rss_id)
        rss_user.save(True)
        payload["rss_id"] = rss_id
    RssTask.parser_feed.delay(source)
    return response_succ(body=payload)


@api.route("/remove", methods=["POST"])
@login_require
def remove():
    """  尝试移除一个订阅源
    Args:
        rss_id: 移除的订阅源
    """
    params = parse_params(request)
    user: User = get_current_user()
    rss_id: Optional[int] = params.get("rss_id")
    if not rss_id:
        return CommonError.get_error(error_code=40000)

    relation_ship: RssUserModel = RssUserModel.query.filter(
        RssUserModel.user_id == user.id, RssUserModel.rss_id == rss_id
    ).one()
    if not relation_ship:
        return CommonError.get_error(error_code=44000)
    session.delete(relation_ship)
    session.commit()
    return response_succ()


@api.route("/limit", methods=["POST"])
@login_require
@pages_info_requires
def rss_list():
    """ 查看订阅列表 """
    params = parse_params(request)
    user: User = get_current_user()
    pageinfo: PageInfo = get_page_info()
    result = (
        session.query(RssModel)
        .filter(
            RssModel.rss_id == RssUserModel.rss_id,
            RssUserModel.user_id == user.id,
            RssUserModel.rss_id == RssModel.rss_id,
        )
        .offset(pageinfo.offset)
        .limit(pageinfo.limit)
        .all()
    )
    payload: List[Dict[AnyStr, any]] = []
    for r in result:
        item = {
            "rss_id": r.rss_id,
            "rss_title": r.rss_title or "",
            "rss_link": r.rss_link,
            "rss_state": int(r.rss_state),
        }
        payload.append(item)
    return response_succ(payload)


@api.route("/content/limit", methods=["GET"])
@login_require
@pages_info_requires
def content_limit():
    params = parse_params(request)
    user: User = get_current_user()
    pageinfo: PageInfo = get_page_info()
    rss_content = (
        session.query(RssContentModel)
        .filter(RssContentModel.rss_id == RssModel.rss_id)
        .filter(RssModel.rss_id == RssUserModel.rss_id)
        .filter(RssUserModel.user_id == user.id)
        .offset(pageinfo.offset)
        .limit(pageinfo.limit)
        .all()
    )
    payload: List[Dict[AnyStr, any]] = []
    for r in rss_content:
        item = {
            "content_id": r.content_id,
            "title": r.content_title or "",
            "link": r.content_link,
            "hover_image": r.content_image_cover or "",
            "description": r.content_description,
        }
        payload.append(item)
    return response_succ(payload)

