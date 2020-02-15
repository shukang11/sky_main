# -*- coding: utf-8 -*-

from typing import Optional, Any, Dict, List, Tuple
from flask import request, Blueprint, Flask
from flask.cli import AppGroup
from app.utils import session, get_logger

from app.model import RssContentModel, RssUserModel, User
import app

GROUPS: List[AppGroup] = []

def regist_group(group: AppGroup):
    global GROUPS
    GROUPS.append(group)

def init_app(app: Flask):
    from . import data

    for cmd in GROUPS:
        app.cli.add_command(cmd)
