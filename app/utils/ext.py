# -*- coding: utf-8 -*-

import os
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound, \
    UnmappedColumnError
from sqlalchemy import Sequence
from flask_sqlalchemy import SQLAlchemy
from redis import ConnectionPool, Redis
from app.config import REDIS_URI
from flask_migrate import Migrate

from celery import Celery

migrate_manager = Migrate()


db: SQLAlchemy = SQLAlchemy()
session = db.session

celery_app = Celery(__name__)

__pool = ConnectionPool.from_url(url=REDIS_URI)
redisClient = Redis(connection_pool=__pool)


__all__ = ['db', 'fileStorage', 'redisClient', 'celery_app']