# -*- coding: utf-8 -*-

from typing import Optional, Dict, Text, AnyStr, List

from app.utils import celery_app
from app.utils import session
from app.utils import get_logger
from app.model import RssModel
from .rss import parser_feed_root, save_feed_items


""" 定时任务队列 """

logger = get_logger(__name__)


@celery_app.task(default_retry_delay=300, max_retries=3, ignore_result=True)
def parse_rsses():
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
