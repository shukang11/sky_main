# -*- coding: utf-8 -*-

from typing import Optional, Dict, Text, AnyStr, List
from flask import current_app
from app.utils import celery_app
from app.utils import session
from app.utils import get_logger, get_unix_time_tuple
from app.model import RssModel, RssContentModel


""" 定时任务队列 """

logger = get_logger(__name__)


@celery_app.task(default_retry_delay=300, max_retries=3, ignore_result=True)
def parse_rsses():
    from .rss import parser_feed_root, save_feed_items

    logger.info("定时任务 === 解析列表中的订阅源")
    rsses: Optional[List[RssModel]] = session.query(RssModel).filter(
        RssModel.rss_state == 1
    ).all()
    links: List[AnyStr] = list(set([r.rss_link for r in rsses]))
    result: bool = True
    for link in links:
        payload = parser_feed_root(link)
        one_res = save_feed_items(link, payload)
        result = result and one_res
        logger.info("{result}--{link}".format(result=one_res, link=link))
    return result


# 每日汇报新增rss情况
@celery_app.task(default_retry_delay=300, max_retries=2, ignore_result=True)
def report_rss_content():
    import datetime
    from sqlalchemy import func
    from flask import render_template
    from .email import send_email

    logger.info("汇报今日Rss爬取状况")
    with current_app.app_context():
        # 获得24小时内新增内容
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(1)
        start_time = get_unix_time_tuple(yesterday)
        rss_content_add_count: int = (
            session.query(RssContentModel)
            .filter(RssContentModel.add_time >= start_time,)
            .with_entities(func.count(RssContentModel.rss_id))
            .scalar()
        )
        # 当前有效订阅源
        rss_enable_count: int = (
            session.query(RssModel)
            .filter(RssModel.rss_state == 1)
            .with_entities(func.count(RssModel.rss_id))
            .scalar()
        )
        # 获得总数
        rss_count: int = (
            session.query(RssContentModel)
            .with_entities(func.count(RssContentModel.rss_id))
            .scalar()
        )
    subject = "测试的主题"
    recip = "804506054@qq.com"
    html = render_template(
        "mail/rss_report.html",
        today_add_count=rss_content_add_count,
        rss_enable_count=rss_enable_count,
        rss_all_count=rss_count,
    )
    send_email(subject=subject, recipients=[recip], sender=sender, html=html)
