# -*- coding: utf-8 -*-

from typing import Optional, AnyStr, TypeVar, Dict
from uuid import uuid4
from sqlalchemy import Column, ForeignKey, String, Sequence
from sqlalchemy import FLOAT, TEXT, INTEGER, DECIMAL, SMALLINT, DateTime
from app.utils import db
from app.utils import get_unix_time_tuple
from .base import BaseModel


class FileModel(db.Model, BaseModel):
    """ 文件映射表 """

    __tablename__ = "bao_file"

    file_id = Column(
        INTEGER,
        Sequence(start=1, increment=1, name="file_id_sep"),
        primary_key=True,
        autoincrement=True,
    )  # 主键
    file_hash = Column(String(64), nullable=False, comment="文件hash值")
    file_name = Column(String(255), nullable=True, comment="文件名")
    file_type = Column(String(32), nullable=True, comment="文件类型")
    file_is_delete = Column(SMALLINT, nullable=True, default=0, comment='删除状态 0 未删除 1 删除')
    file_create_time = Column(String(10), nullable=True, default=get_unix_time_tuple)

    def __init__(
        self,
        file_name: str,
        file_type: Optional[str] = None,
        file_hash: Optional[str] = None,
        file_is_delete: bool = False,
    ):
        self.file_name = file_name
        self.file_type = file_type
        self.file_hash = file_hash or str(uuid4()).replace("-", "")
        self.file_is_delete = int(file_is_delete)


class FileUserModel(db.Model, BaseModel):
    """ 文件与用户映射 """

    __tablename__ = "bao_file_user"

    file_user_id = Column(
        INTEGER,
        Sequence(start=1, increment=1, name="file_user_id_sep"),
        primary_key=True,
        autoincrement=True,
    )
    user_id = Column(INTEGER, nullable=False)
    file_id = Column(INTEGER, nullable=False, comment="文件id")
    add_time = Column(String(10), nullable=True, default=get_unix_time_tuple, comment="添加时间")
    file_user_state = Column(SMALLINT, nullable=True, comment="1 创建(未验证) 2 有效 3 失效 4 删除")

    def __init__(self, user_id: int, file_id: int):
        self.user_id = user_id
        self.file_id = file_id
        self.file_user_state = 1
