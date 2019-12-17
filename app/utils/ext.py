# -*- coding: utf-8 -*-

import os
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound, \
    UnmappedColumnError
from sqlalchemy import Sequence
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, DEFAULTS, configure_uploads
from redis import ConnectionPool, Redis

from flask_migrate import Migrate

from celery import Celery

migrate_manager = Migrate()

REDIS_HOST = os.environ.get('REDIS_HOST', '0.0.0.0')

db: SQLAlchemy = SQLAlchemy()
session = db.session

celery_app = Celery(__name__)

fileStorage = UploadSet(extensions=DEFAULTS)

__pool = ConnectionPool(host=REDIS_HOST, port=6379)
redisClient = Redis(connection_pool=__pool)

__all__ = ['db', 'fileStorage', 'redisClient', 'celery_app']