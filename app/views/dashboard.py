# -*- coding: utf-8 -*-

from typing import Any, Dict
import datetime
from flask import Blueprint
from app.utils import response_error, response_succ
from app.utils import get_random_num, get_unix_time_tuple, getmd5
from app.utils import session, parse_params, get_current_user
from app.utils import login_require, pages_info_requires, get_page_info, PageInfo
from app.utils import get_logger
from app.model import User, RssContentModel, RssModel, RssReadRecordModel, RssUserModel

api = Blueprint("dashboard", __name__)

logger = get_logger(__name__)


@login_require
def dashboard_info():
    user: User = get_current_user()
    payload: Dict[str, Any] = {}
    # 获得今日新增内容
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(1)
    start_time = get_unix_time_tuple(yesterday)
    rss_content_count: int = (
        session.query(RssContentModel)
        .filter(
            RssContentModel.rss_id == RssModel.rss_id,
            RssModel.rss_id == RssUserModel.rss_id,
            RssUserModel.user_id == user.id,
            RssContentModel.add_time >= start_time,
        )
        .count()
    )
    payload.setdefault("today_rss_content_count", rss_content_count)
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
    # 获得总数
    rss_count: int = (
        session.query(RssContentModel)
        .filter(
            RssContentModel.rss_id == RssModel.rss_id,
            RssModel.rss_id == RssUserModel.rss_id,
            RssUserModel.user_id == user.id,
        )
        .count()
    )
    payload.setdefault("rss_count", rss_count)
    return response_succ(body=payload)


def setup_url_rule(api: Blueprint):
    api.add_url_rule("/info", view_func=dashboard_info, methods=["GET", "POST"])


setup_url_rule(api)
