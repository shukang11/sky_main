# -*- coding: utf-8 -*-

from typing import Optional, Any, Dict, List, Tuple
from flask import request, Blueprint
from flask.cli import AppGroup
from app.utils import session, get_logger

from app.model import RssContentModel, RssUserModel, User
import app

cmd = AppGroup("data")

logger = get_logger(__name__)

@cmd.command("export")
def export_rss_data():
    """ 导出数据 """
    # 获得订阅数据
    all_content = session.query(RssContentModel).all()
    logger.info(all_content)


