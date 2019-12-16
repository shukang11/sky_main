# -*- coding: utf-8 -*-

from typing import Optional, AnyStr, TypeVar, Dict
from sqlalchemy import Column, ForeignKey, String, Sequence
from sqlalchemy import FLOAT, TEXT, INTEGER, DECIMAL, SMALLINT, Table
from app.utils import db
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

    def __init__(self, link: str, add_time: Optional[AnyStr] = None):
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

    def __init__(self, user_id: int, rss_id: int, add_time: Optional[AnyStr] = None):
        self.user_id = user_id
        self.rss_id = rss_id
        self.rss_user_state = 1
        self.add_time = add_time


class RssContentModel(db.Model, BaseModel):

    __tablename__ = "bao_rss_content"

    content_id = Column(
        INTEGER,
        Sequence(start=1, increment=1, name="content_id_sep"),
        primary_key=True,
        autoincrement=True,
    )
    content_base = Column(String(255), nullable=True)
    content_link = Column(String(255), nullable=True)
    content_title = Column(String(255), nullable=True)
    content_description = Column(TEXT, nullable=True)
    content_image_cover = Column(String(255), nullable=True)
    published_time = Column(String(64), nullable=True)
    add_time = Column(String(20), nullable=True)

    def __init__(
        self,
        link: str,
        baseurl: str,
        title: str,
        description: str,
        cover_img: str,
        published_time: str,
        add_time: Optional[AnyStr] = None,
    ):
        self.content_link = link
        self.content_base = baseurl
        self.content_title = title
        self.published_time = published_time
        self.content_image_cover = cover_img
        self.content_description = description
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

    def __init__(self, url_id: int, user_id: int, read_at: Optional[AnyStr] = None):
        self.read_url_id = url_id
        self.read_user_id = user_id
        self.read_time = read_at


class TaskModel(db.Model, BaseModel):
    """ 包含了任务发起者，开始时间, 结束时间 状态等 """
    __tablename__ = 'bao_task_record'

    task_id = Column(String(125), primary_key=True)
    tast_name = Column(String(255))
    argsrepr = Column(String(255))
    kwargs = Column(String(255))
    user_id = Column(INTEGER)
    begin_at = Column(String(20))
    end_at = Column(String(20))
    is_succ = Column(SMALLINT)
