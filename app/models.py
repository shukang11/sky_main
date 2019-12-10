from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.mssql import FLOAT, TEXT, INTEGER, DECIMAL, SMALLINT

from app.utils.helpers import db
from app.utils.strings import get_unix_time_tuple

"""
doc: http://docs.jinkan.org/docs/flask-sqlalchemy/models.html
"""

__all__ = []


def addModel(model):
    __all__.append(model.__name__)


class BaseModel():
    """
    基类，在此封装一层
    可以提供一些基本的功能
    """


@addModel
class User(db.Model, BaseModel):
    """ 用户信息表 """
    __tablename__ = "bao_user"

    id = Column(INTEGER, Sequence(start=1, increment=1,
                                  name="file_id_sep"), primary_key=True, doc='主键', comment='主键')
    # 性别
    isMan = Column(SMALLINT, default=0, doc='性别', comment=' 0 未设置 1 男性 2 女性')
    # 邮箱
    email = Column(String(100), unique=True, doc='邮箱', comment=' 邮箱')
    # 昵称
    nickname = Column(String(18), nullable=True, doc='昵称', comment='中文与英文符合混合')
    # 密码 md5 加密文
    password = Column(String(255), nullable=True, doc='密码', comment='MD5加密值')
    # 用户状态
    status = Column(SMALLINT, default=0, doc='用户状态', comment='0 未激活 1 正常 2...')


@addModel
class UserToken(db.Model, BaseModel):
    """ 用户与token之间的关联表 """
    __tablename__ = 'bao_user_token'

    user_id = Column(INTEGER, Sequence(start=1, increment=1,
                                       name="file_id_sep"), primary_key=True, autoincrement=True, doc='用户主键',
                     comment='用户主键，需要关联用户的token')
    user_token = Column(String(64), nullable=True,
                        doc='用户token', comment='会根据最后的登录信息，更新用户的token')
    update_time = Column(String(11), nullable=True,
                         doc='更新时间', comment='每次变更都会更新此值')


@addModel
class LoginRecord(db.Model, BaseModel):
    """ 登录记录表 """

    __tablename__ = "bao_login_record"

    record_id = Column(INTEGER, Sequence(start=1, increment=1,
                                         name="record_id_sep"), primary_key=True, autoincrement=True)
    user_id = Column(INTEGER)
    login_time = Column(String(20), nullable=True, comment='登录时间')
    log_ip = Column(String(20), nullable=True, comment='登录ip')


@addModel
class FileModel(db.Model, BaseModel):
    """ 文件映射表 """

    __tablename__ = "bao_file"

    file_id = Column(INTEGER, Sequence(start=1, increment=1,
                                       name="file_id_sep"), primary_key=True, autoincrement=True)  # 主键
    file_hash = Column(String(64), nullable=False,
                       doc='hash值', comment='文件的hash值，上传文件的时候会生成')
    file_name = Column(String(255), nullable=True,
                       doc='文件名', comment='如果没有指定文件名，则会随机生成一个')
    file_type = Column(String(32), nullable=True,
                       doc='文件类型', comment='指的是文件的mimetype')


@addModel
class FileUserModel(db.Model, BaseModel):
    """ 文件与用户映射 """
    __tablename__ = "bao_file_user"

    file_user_id = Column(INTEGER, Sequence(start=1, increment=1,
                                            name="file_user_id_sep"), primary_key=True, autoincrement=True)
    user_id = Column(INTEGER, nullable=False, comment='用户id')
    file_id = Column(INTEGER, nullable=False, comment='文件id')
    add_time = Column(String(20), nullable=True, comment='创建时间')
    file_user_state = Column(
        SMALLINT, default=1, nullable=True, comment='0 创建 1 损坏或丢失')

    def __init__(self, user_id: int, file_id: int, add_time: str = None):
        self.user_id = user_id
        self.file_id = file_id
        self.file_user_state = 1
        self.add_time = add_time or get_unix_time_tuple()
