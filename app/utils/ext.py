# -*- coding: utf-8 -*-

import os
from flask import Flask
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound, \
    UnmappedColumnError
from sqlalchemy import Sequence
from flask_sqlalchemy import SQLAlchemy
from redis import ConnectionPool, Redis

from celery import Celery

db: SQLAlchemy = SQLAlchemy()
session = db.session

celery_app = Celery(__name__)


__all__ = ['db', 'fileStorage', 'celery_app']

def init_app(app: Flask):
    url: str = app.config.get('REDIS_URI')
    print(url)
    __pool = ConnectionPool.from_url(url)  
    redisClient = Redis(connection_pool=__pool)
    app.redisClient = redisClient