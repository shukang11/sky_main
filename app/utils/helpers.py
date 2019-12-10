"""
Helper functions
"""

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound, \
    UnmappedColumnError
from sqlalchemy import Sequence
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, DEFAULTS, configure_uploads

db: SQLAlchemy = SQLAlchemy()
fileStorage = UploadSet(extensions=DEFAULTS)

__all__ = ['db', 'fileStorage']