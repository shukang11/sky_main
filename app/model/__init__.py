# -*- coding: utf-8 -*-


"""
doc: http://docs.jinkan.org/docs/flask-sqlalchemy/models.html
"""
from flask import Flask
from flask_migrate import Migrate

from app.utils import db

from .user import User, LoginRecordModel
from .todo import TodoModel
from .rss import (
    RssContentModel,
    RssModel,
    RssReadRecordModel,
    RssUserModel,
    RssContentCollectModel,
)
from .file import FileModel, FileUserModel

__all__ = [
    "User",
    "LoginRecordModel",
    "TodoModel",
    "RssContentModel",
    "RssModel",
    "RssReadRecordModel",
    "RssUserModel",
    "RssContentCollectModel",
    "FileModel",
    "FileUserModel"
]

def init_app(app: Flask, env: str):
    db.init_app(app)
    if env == "testing":
        @app.before_first_request
        def create_all():
            db.create_all(app=app)
    Migrate(app=app, db=db)
