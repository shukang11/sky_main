# -*- coding: utf-8 -*-

from typing import Optional, Any, Dict, List, Tuple
from flask.cli import AppGroup
import pandas as pd
from app.utils import session, get_logger

from app.model import RssContentModel, RssUserModel, User
import app

from ..scripts import regist_group

cmd = AppGroup("data")
regist_group(cmd)

logger = get_logger(__name__)

@cmd.command("export")
def export_rss_data():
    """ 导出数据 """
    # 获得订阅数据
    logger.info("export_rss_data")
    all_content: List[RssContentModel] = session.query(RssContentModel).all()
    content: List[Dict[str, Any]] = [{'id': row.content_id, 'title': row.content_title, 'site': row.content_link} for row in all_content]
    df = pd.DataFrame(content, columns=['id', 'title', 'site'])
    df.to_csv("export.csv")