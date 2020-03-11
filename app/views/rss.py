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
from app.utils import is_link, get_logger
from app.task import rss as RssTask
from app.model import (
    User,
    RssContentModel,
    RssModel,
    RssReadRecordModel,
    RssUserModel,
    RssContentCollectModel,
)

api = Blueprint("rss", __name__)

logger = get_logger(__name__)


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
    try:
        rss_content: List[Tuple[str, ...]] = (
            session.query(
                RssContentModel.content_id.label("cid"),
                RssContentModel.rss_id.label("rssId"),
                RssContentModel.content_link.label("link"),
                RssContentModel.content_title.label("title"),
                RssContentModel.content_image_cover.label("image"),
                RssContentModel.published_time.label("publishDate"),
                RssContentModel.add_time.label("addDate"),
                RssModel.rss_title.label("fromsite"),
                RssContentCollectModel.is_collected.label("isCollected"),
            )
            .join(
                RssUserModel,
                and_(
                    RssUserModel.rss_id == RssContentModel.rss_id,
                    RssUserModel.user_id == user.id,
                ),
                isouter=False,
            )
            .join(RssModel, RssContentModel.rss_id == RssModel.rss_id, isouter=False)
            .outerjoin(
                RssContentCollectModel,
                RssContentCollectModel.content_id == RssContentModel.content_id,
            )
            .order_by(RssContentModel.published_time.desc())
            .offset(pageinfo.offset)
            .limit(pageinfo.limit)
            .all()
        )
    except Exception as e:
        logger.error(e)
        return CommonError.get_error(error_code=9999)
    else:
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


def setup_blueprint(api: Blueprint):
    # 添加一个订阅源
    api.add_url_rule("/add", view_func=add_rss_source, methods=["POST"])
    # 试移除一个订阅源
    api.add_url_rule("/remove", view_func=remove, methods=["POST"])
    # 查看订阅源列表
    api.add_url_rule("/limit", view_func=rss_list, methods=["GET"])
    # 订阅内容的列表
    api.add_url_rule("/content/limit", view_func=content_limit, methods=["GET"])
    # 添加阅读记录
    api.add_url_rule(
        "/content/reading/<int:content_id>",
        view_func=rss_content_read,
        methods=["POST"],
    )
    # 收藏内容或取消收藏
    api.add_url_rule(
        "/content/toggleCollect/<int:content_id>",
        view_func=rss_collect,
        methods=["POST"],
    )


setup_blueprint(api)
