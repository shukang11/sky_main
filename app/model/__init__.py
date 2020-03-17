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
from flask_sqlalchemy import get_debug_queries

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
    "FileUserModel",
]


def init_app(app: Flask, env: str):
    db.init_app(app)
    if env != "product":

        @app.before_first_request
        def create_all():
            db.create_all(app=app)

        @app.after_request
        def query_time_out(response):
            for query in get_debug_queries():
                if query.duration >= 0.05:
                    app.logger.warn(
                        "Context: {} \n SLOW QUERY: {} \n Parameters: {} \n Duration: {} \n".format(
                            query.context,
                            query.statement,
                            query.parameters,
                            query.duration,
                        )
                    )
            return response

    Migrate(app=app, db=db)
