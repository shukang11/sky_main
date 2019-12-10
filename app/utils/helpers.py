"""
Helper functions
"""

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound, \
    UnmappedColumnError
from sqlalchemy import Sequence
from flask_sqlalchemy import SQLAlchemy

db: SQLAlchemy = SQLAlchemy()

__all__ = ['db']