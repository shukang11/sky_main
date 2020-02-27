# -*- coding: utf-8 -*-

from typing import Optional, AnyStr, TypeVar, Dict
from uuid import uuid4
from sqlalchemy import Column, ForeignKey, String, Sequence, Text
from sqlalchemy import FLOAT, TEXT, INTEGER, DECIMAL, SMALLINT, BOOLEAN
from sqlalchemy.orm import relationship
from app.utils import db
from app.utils import get_unix_time_tuple
from .base import BaseModel


class Article(db.Model, BaseModel):
    """ 博客文章模型 """

    __tablename__ = "blog_article"

    article_id = Column(
        INTEGER,
        Sequence(start=1, increment=1, name="article_id_sep"),
        primary_key=True,
        autoincrement=True,
    )  # 主键
    user_id = Column(INTEGER, nullable=False, comment="用户id")
    content = Column(Text, nullable=False, comment="文章内容")
    title = Column(String(255), nullable=False, comment="文章标题")
    create_time = Column(String(10), nullable=True, default=get_unix_time_tuple)
    is_delete = Column(BOOLEAN, nullable=True, default=False, comment="删除状态")
    is_publish = Column(BOOLEAN, nullable=True, default=False, comment="是否发布")

    def __init__(
        self, user_id: int, title: str, content: str, is_publish: Optional[bool] = None
    ):
        self.user_id = user_id
        self.title = title
        self.content = content
        self.is_publish = is_publish
