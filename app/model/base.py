# -*- coding: utf-8 -*-

from app.utils import db

class BaseModel():
    def save(self, commit: bool=False):
        """  保存模型到数据库
        Args:
            commit: 是否立即提交
        """
        db.session.add(self)
        if commit: db.session.commit()
