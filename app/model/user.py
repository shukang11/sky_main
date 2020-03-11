# -*- coding: utf-8 -*-
from uuid import uuid4
from typing import Optional, ClassVar, Dict, Any
from sqlalchemy import Column, ForeignKey, String, Sequence
from sqlalchemy import FLOAT, TEXT, INTEGER, DECIMAL, SMALLINT, Table
from app.utils import db
from .base import BaseModel


class User(db.Model, BaseModel):
    __tablename__ = "bao_user"

    id = Column(
        INTEGER,
        Sequence("user_id_seq", start=1, increment=1),
        primary_key=True,
        comment="用户的id",
    )
    sex = Column(SMALLINT, nullable=True, default=0, comment="0 未设置 1 男性 2 女性")
    identifier = Column(String(128), nullable=True, comment="用户的标识符，在某些情况不适合用id，会用此字段")
    mobilephone = Column(String(11), nullable=True)
    nickname = Column(String(18), nullable=True, comment="用户昵称")
    email = Column(String(64), nullable=True, unique=True)
    password = Column(String(64), nullable=True)
    status = Column(SMALLINT, nullable=True, default=1, comment="0 未激活 1 正常 2 异常 3 注销")

    def __init__(
        self,
        email: Optional[str] = None,
        sex: int = 0,
        mobilephone: Optional[str] = None,
        nickname: Optional[str] = None,
        password: Optional[str] = None,
        status: int = 1,
        identifier: Optional[str] = None,
    ):
        """  初始化方法
        在注册时使用，其中 email 是必须的
        """
        if not email or mobilephone:
            raise ValueError("email 或 mobilephone 不能为空")
        self.email = email
        self.mobilephone = mobilephone
        self.nickname = nickname
        self.password = password
        self.status = status
        self.sex = sex
        self.identifier = identifier or str(uuid4())

    @classmethod
    def get_user(
        cls, uid: Optional[int] = None, identifier: Optional[str] = None
    ) -> Optional['User']:
        """  从表中查询用户实例
        Args:
            uid: 用户id
            identifier: 用户id别名
        Return: 
            用户的实例，如果没有找到则返回None
        """
        try:
            if uid:
                return User.query.filter(User.id == uid).one()
            if identifier:
                return User.query.filter(User.identifier == identifier).one()
            return None
        except Exception as e:
            print(e)
            return None

    @property
    def get_cache_key(self) -> str:
        return (
            str(self.identifier)
            if self.identifier
            else "sky_user_cache_key_{user_id}".format(user_id=self.id)
        )

    @property
    def info_dict(self) -> Dict[str, Any]:
        """  将用户信息组装成字典
        """
        payload: Dict[str, Any] = {
            "user_id": self.id,
            "sex": self.sex or 0,
            "email": self.email or "",
            "phone": self.mobilephone or "",
            "account_status": self.status or 0,
            "nickname": self.nickname,
        }
        return payload


class LoginRecordModel(db.Model, BaseModel):
    __tablename__ = "bao_login_record"

    record_id = Column(
        INTEGER,
        Sequence("login_record_id_seq", start=1, increment=1),
        primary_key=True,
        comment="用户的登录记录",
    )
    user_id = Column(INTEGER, nullable=True)
    op_time = Column(String(20), nullable=True)
    op_ip = Column(String(20), nullable=True)

    def __init__(
        self, user_id: int, op_ip: Optional[str] = None, op_time: Optional[str] = None,
    ):
        from app.utils import get_unix_time_tuple

        self.user_id = user_id
        self.op_time = op_time or get_unix_time_tuple()
        self.op_ip = op_ip
