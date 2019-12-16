# -*- coding: utf-8 -*-

from typing import Optional, AnyStr, TypeVar, Dict
from sqlalchemy import Column, ForeignKey, String, Sequence
from sqlalchemy import FLOAT, TEXT, INTEGER, DECIMAL, SMALLINT, Table
from app.utils import db
from .base import BaseModel

class TodoModel(db.Model, BaseModel):
    """ Todo list """
    __tablename__ = "bao_todo"

    todo_id = Column(INTEGER, Sequence(start=1, increment=1,
                                       name="todo_id_sep"), primary_key=True, autoincrement=True)
    todo_title = Column(String(255), nullable=True, comment='待办标题')
    add_time = Column(String(20), nullable=True, comment='添加时间')
    bind_user_id = Column(INTEGER, nullable=True, comment='绑定用户id')
    todo_state = Column(SMALLINT, nullable=True, comment=' # 1 创建 2 完成 3 删除')
