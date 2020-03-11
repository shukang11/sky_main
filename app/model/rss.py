# -*- coding: utf-8 -*-

from typing import Optional, TypeVar, Dict
from sqlalchemy import Column, ForeignKey, String, Sequence
from sqlalchemy import FLOAT, TEXT, INTEGER, DECIMAL, SMALLINT, Table, Boolean
from app.utils import db, get_unix_time_tuple
from .base import BaseModel


class RssModel(db.Model, BaseModel):
    """ rss 订阅 """

    __tablename__ = "bao_rss"

    rss_id = Column(
        INTEGER,
        Sequence(start=1, increment=1, name="rss_id_sep"),
        primary_key=True,
        autoincrement=True,
    )
    rss_link = Column(String(255), nullable=True)
    rss_subtitle = Column(String(255), nullable=True)
    add_time = Column(String(20), nullable=True)
    rss_version = Column(String(10), nullable=True)
    rss_title = Column(String(255), nullable=True, comment="订阅的标题")
    rss_state = Column(SMALLINT, nullable=True, comment="# 1 创建(未验证) 2 有效 3 失效")

    def __init__(self, link: str, add_time: Optional[str] = None):
        self.rss_link = link
        self.rss_state = 1
        self.add_time = add_time


class RssUserModel(db.Model, BaseModel):
    """ rss 与用户映射 """

    __tablename__ = "bao_rss_user"

    rss_user_id = Column(
        INTEGER,
        Sequence(start=1, increment=1, name="rss_user_id_sep"),
        primary_key=True,
        autoincrement=True,
    )
    user_id = Column(INTEGER, nullable=False)
    rss_id = Column(INTEGER, nullable=False)
    add_time = Column(String(20), nullable=True)
    rss_user_state = Column(SMALLINT, nullable=True, comment="# 1 创建(未验证) 2 有效 3 失效")

    def __init__(self, user_id: int, rss_id: int, add_time: Optional[str] = None):
        self.user_id = user_id
        self.rss_id = rss_id
        self.rss_user_state = 1
        self.add_time = add_time or get_unix_time_tuple()


class RssContentModel(db.Model, BaseModel):

    __tablename__ = "bao_rss_content"

    content_id = Column(
        INTEGER,
        Sequence(start=1, increment=1, name="content_id_sep"),
        primary_key=True,
        autoincrement=True,
    )
    rss_id = Column(INTEGER, comment="属于哪一个订阅的内容")
    content_link = Column(String(255), nullable=True)
    content_title = Column(String(255), nullable=True)
    content_image_cover = Column(String(255), nullable=True)
    published_time = Column(String(64), nullable=True)
    add_time = Column(String(20), nullable=True)

    def __init__(
        self,
        link: str,
        pid: int,
        title: str,
        cover_img: str,
        published_time: str,
        add_time: Optional[str] = None,
    ):
        self.content_link = link
        self.rss_id = pid
        self.content_title = title
        self.published_time = published_time
        self.content_image_cover = cover_img
        self.add_time = add_time


class RssReadRecordModel(db.Model, BaseModel):
    __tablename__ = "bao_rss_read_record"

    read_id = Column(
        INTEGER,
        Sequence(start=1, increment=1, name="read_id_sep"),
        primary_key=True,
        autoincrement=True,
    )
    read_url_id = Column(INTEGER, nullable=False)
    read_user_id = Column(INTEGER)
    read_time = Column(String(20), nullable=True)

    def __init__(self, url_id: int, user_id: int, read_at: Optional[str] = None):
        self.read_url_id = url_id
        self.read_user_id = user_id
        self.read_time = read_at or get_unix_time_tuple()


class RssContentCollectModel(db.Model, BaseModel):
    """ rss内容收藏记录 """

    __tablename__ = "bao_rss_content_collect"

    collect_id = Column(
        INTEGER,
        Sequence(start=1, increment=1, name="collect_id_sep"),
        primary_key=True,
        autoincrement=True,
    )
    user_id = Column(INTEGER, nullable=True)
    content_id = Column(INTEGER, nullable=True)
    collect_time = Column(String(11), nullable=True)
    is_collected = Column(Boolean, nullable=True, default=False, comment="1 收藏 0 删除 未收藏")

    def __init__(self, content_id: int, user_id: int, time: Optional[str] = None):
        self.content_id = content_id
        self.user_id = user_id
        self.collect_time = time or get_unix_time_tuple()
        self.is_delete = 0
