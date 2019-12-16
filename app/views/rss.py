# -*- coding: utf-8 -*-

from typing import Optional, AnyStr, Dict
from flask import request, Blueprint
from sqlalchemy import and_
from app.utils import UserError, CommonError
from app.utils import response_error, response_succ
from app.utils import get_random_num, get_unix_time_tuple, getmd5
from app.utils import session, parse_params, get_current_user
from app.utils import login_require
from app.utils import is_link, get_logger
from app.task.sample import reversed as rev
from app.model import User, RssContentModel, RssModel, RssReadRecordModel, RssUserModel
import app

api = Blueprint("rss", __name__)
app.fetch_route(api, "/rss")

loger = get_logger(__name__)


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
        and_(RssUserModel.user_id == user.id, RssUserModel.rss_id == rss_id)
    ).first()
    payload: Dict[AnyStr, any] = {}
    if exsits_relationship:
        payload["rss_id"] = rss_id
    else:
        rss_user = RssUserModel(user.id, rss_id)
        rss_user.save(True)
        payload["rss_id"] = rss_id
    return response_succ(body=payload)
