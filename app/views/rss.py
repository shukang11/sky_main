# -*- coding: utf-8 -*-

from typing import Optional, Any, Dict, List, Tuple
from flask import request, Blueprint
from sqlalchemy import and_, outerjoin
from app.utils import NoResultFound, MultipleResultsFound
from app.utils import UserError, CommonError
from app.utils import response_error, response_succ
from app.utils import (
    get_unix_time_tuple,
    get_date_from_time_tuple,
)
from app.utils import session, parse_params, get_current_user
from app.utils import login_require, pages_info_requires, get_page_info, PageInfo
from app.utils import is_link, get_logger, redisClient
from app.task import rss as RssTask
from app.model import (
    User,
    RssContentModel,
    RssModel,
    RssReadRecordModel,
    RssUserModel,
    RssContentCollectModel,
    RssContentRateModel,
)
import app

api = Blueprint("rss", __name__)
app.fetch_route(api, "/rss")

logger = get_logger(__name__)


@api.route("/add/", methods=["POST"])
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

    rss_id: Optional[int]
    # 检查是否存在rss
    try:
        exists_rss: RssModel = RssModel.query.filter(RssModel.rss_link == source).one()
        if exists_rss:
            rss_id = exists_rss.rss_id
    except MultipleResultsFound as e:
        # 如果存在多个记录，要抛出
        logger.error(e)
        return response_error(error_code=9999)
    except NoResultFound:
        rss = RssModel(source, add_time=get_unix_time_tuple())
        session.add(rss)
        session.flush()
        rss_id = rss.rss_id
    # 是否存在关系
    exsits_relationship: RssUserModel = RssUserModel.query.filter(
        RssUserModel.user_id == user.id, RssUserModel.rss_id == rss_id
    ).first()
    payload: Dict[str, any] = {}
    if exsits_relationship:
        payload["rss_id"] = rss_id
    else:
        rss_user = RssUserModel(user.id, rss_id)
        rss_user.save(True)
        payload["rss_id"] = rss_id
    RssTask.parser_feed.delay(source)
    return response_succ(body=payload)


@api.route("/remove/", methods=["POST"])
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


@api.route("/limit/", methods=["GET"])
@login_require
@pages_info_requires
def rss_list():
    """ 查看订阅源列表 """
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
    payload: List[Dict[str, Any]] = []
    for r in result:
        item = {
            "rss_id": r.rss_id,
            "rss_title": r.rss_title or "",
            "rss_link": r.rss_link,
            "rss_state": int(r.rss_state),
        }
        payload.append(item)
    return response_succ(body=payload)


@api.route("/content/limit/", methods=["GET"])
@login_require
@pages_info_requires
def content_limit():
    """  获得订阅内容的列表
    Args:
        包含分页信息
    """
    params = parse_params(request)
    user: User = get_current_user()
    pageinfo: PageInfo = get_page_info()
    sql: str = (
        "SELECT bao_rss_content.content_id AS cid, " 
        "bao_rss_content.rss_id AS rssId, " 
        "bao_rss_content.content_link AS link, " 
        "bao_rss_content.content_title AS title, " 
        "bao_rss_content.content_image_cover AS image, " 
        "bao_rss_content.published_time AS publishDate, " 
        "bao_rss_content.add_time AS addDate, " 
        "bao_rss.rss_title AS fromsite, "
        "bao_rss_content_collect.is_collected AS isCollected "
        "FROM bao_rss_content "
        "LEFT JOIN bao_rss_user ON bao_rss_content.rss_id = bao_rss_user.rss_id AND bao_rss_user.user_id = {uid} " 
        "LEFT JOIN bao_rss ON bao_rss_content.rss_id = bao_rss.rss_id "
        "INNER JOIN bao_rss_content_collect ON bao_rss_content_collect.content_id = bao_rss_content.content_id "
        "ORDER BY bao_rss_content.published_time DESC "
        "LIMIT {offset}, {limit}; "
    ).format(uid=user.id, offset=pageinfo.offset, limit=pageinfo.limit)
    logger.info(sql)
    rss_content: Any = session.execute(sql)
    logger.info(rss_content)
    payload: List[Dict[str, Any]] = []
    for item in rss_content:
        item = {
            "content_id": item.cid,
            "title": item.title or "",
            "link": item.link,
            "hover_image": item.image or "",
            "add_time": get_date_from_time_tuple(item.addDate),
            "from_site": item.fromsite,
            "isCollected": item.isCollected,
            # "rate_value": rate_value,
            # "is_no_rate": not rate_value,
        }
        payload.append(item)
    return response_succ(body=payload)


@api.route("/content/reading/<int:content_id>/", methods=["POST"])
@login_require
def rss_content_read(content_id: Optional[int] = None):
    """  添加阅读记录
    """
    user: User = get_current_user()
    if not content_id:
        return CommonError.get_error(error_code=40000)
    record = RssReadRecordModel(url_id=content_id, user_id=user.id)
    record.save(commit=True)
    return response_succ()


@api.route("/content/toggleCollect/<int:content_id>/", methods=["POST"])
@login_require
def rss_collect(content_id: Optional[int] = None):
    """  收藏内容或取消收藏
    """
    user: User = get_current_user()
    if not content_id:
        return CommonError.get_error(error_code=40000)
    model: RssContentCollectModel
    try:
        model = RssContentCollectModel.query.filter(
            RssContentCollectModel.user_id == user.id,
            RssContentCollectModel.content_id == content_id,
        ).one()
        isCollect: bool = bool(model.is_collected)
        model.is_collected = int(not isCollect)
    except NoResultFound:
        model = RssContentCollectModel(content_id, user.id)
        model.is_collected = 1
    session.flush()
    toast: str = "收藏成功" if model.is_collected else "取消成功"
    result: Dict[str, Any] = {
        "contentId": content_id,
        "userId": user.id,
        "isCollected": model.is_collected,
    }
    model.save(commit=True)
    return response_succ(body=result, toast=toast)


@api.route("/content/rate/<int:content_id>/<int:rate_value>", methods=["POST"])
@login_require
def rss_rate(content_id: int, rate_value: int):
    """ 对订阅内容评分 """
    user: User = get_current_user()
    params: Dict[str, str] = parse_params(request)
    if not user:
        return CommonError.get_error(error_code=40000)
    model: RssContentRateModel
    try:
        model = RssContentRateModel.query.filter(
            RssContentRateModel.content_id, RssContentRateModel.user_id == user.id
        ).one()
    except NoResultFound:
        model = RssContentRateModel(content_id, user.id, None, params.get("content"))
    except MultipleResultsFound:
        return CommonError.get_error(error_code=40000)
    else:
        model.save(commit=True)
    payload: Dict[str, int] = {}
    payload["content_id"] = content_id
    payload["rate_value"] = rate_value
    return response_succ(payload)
