# -*- coding: utf-8 -*-

from flask import Flask

from .errors import CommonError, UserError

from .ext import session
from .ext import db
from .ext import celery_app
from .ext import redis_client
from .ext import mail_client

from .ext import NoResultFound, MultipleResultsFound, UnmappedColumnError

from .helpers import parse_params, get_current_user
from .helpers import get_logger, get_page_info, PageInfo

from .response import response_error, response_succ, page_wrapper

from .strings import get_date_from_time_tuple
from .strings import get_unix_time_tuple
from .strings import get_random_num, getmd5
from .strings import get_domain
from .strings import filter_all_img_src
from .strings import contain_emoji
from .regex import is_emoji
from .regex import is_link
from .regex import is_phone, is_email

from .verfy import login_option, login_require
from .verfy import pages_info_requires

from sqlalchemy import text


def init_app(app: Flask):
    from . import ext
    ext.init_app(app)