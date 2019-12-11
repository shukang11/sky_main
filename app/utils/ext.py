# -*- coding: utf-8 -*-

import os
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound, \
    UnmappedColumnError
from sqlalchemy import Sequence
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, DEFAULTS, configure_uploads
from redis import ConnectionPool, Redis


REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')


db: SQLAlchemy = SQLAlchemy()

fileStorage = UploadSet(extensions=DEFAULTS)

__pool = ConnectionPool(host=REDIS_HOST, port=6379)
redisClient = Redis(connection_pool=__pool)

__all__ = ['db', 'fileStorage', 'redisClient']