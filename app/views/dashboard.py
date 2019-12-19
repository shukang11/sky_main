# -*- coding: utf-8 -*-

from typing import Optional, AnyStr, Dict, List
import datetime
from flask import request, Blueprint
from app.utils import UserError, CommonError
from app.utils import response_error, response_succ
from app.utils import get_random_num, get_unix_time_tuple, getmd5
from app.utils import session, parse_params, get_current_user
from app.utils import login_require, pages_info_requires, get_page_info, PageInfo
from app.utils import is_link, get_logger
from app.task import rss as RssTask
from app.model import User, RssContentModel, RssModel, RssReadRecordModel, RssUserModel
import app

api = Blueprint("dashboard", __name__)
app.fetch_route(api, "/dashboard")

logger = get_logger(__name__)


@login_require
def dashboard_info():
    user: User = get_current_user()
    payload: Dict[AnyStr, str] = {}
    # 获得今日新增内容
    today = get_unix_time_tuple(datetime.date.today())
    logger.info(today)
    rss_content = (
        session.query(RssContentModel)
        .filter(RssContentModel.rss_id == RssModel.rss_id)
        .filter(RssModel.rss_id == RssUserModel.rss_id)
        .filter(RssUserModel.user_id == user.id)
        # .filter(RssContentModel.add_time >= today)
        .count()
    )
    payload.setdefault("today_rss_content_count", rss_content)
    # 当前有效订阅源
    rss_enable_count = (
        session.query(RssModel)
        .filter(
            RssModel.rss_state == 1,
            RssModel.rss_id == RssUserModel.rss_id,
            RssUserModel.user_id == user.id,
        )
        .count()
    )
    payload.setdefault("rss_enable_count", rss_enable_count)
    return response_succ(body=payload)


api.add_url_rule("/info", view_func=dashboard_info, methods=["GET", "POST"])
