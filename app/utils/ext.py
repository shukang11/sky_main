# -*- coding: utf-8 -*-

import os
from typing import Optional, Union, Dict, Any
from flask import Flask
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound, UnmappedColumnError
from sqlalchemy import Sequence
from flask_sqlalchemy import SQLAlchemy
from app.extension.ext_redis import FlaskRedis
from celery import Celery



db: SQLAlchemy = SQLAlchemy()
session = db.session

celery_app = Celery(__name__)

redis_client = FlaskRedis(config_key="REDIS_URI")

__all__ = ["db", "fileStorage", "celery_app", "redis_client"]


def init_app(app: Flask):
    redis_client.init_app(app)
