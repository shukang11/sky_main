# -*- coding: utf-8 -*-

from os import path, listdir
from typing import Any, List, Tuple

from flask import Flask, Blueprint

from app.utils import get_logger
from app.utils import celery_app
from . import config, cold_data
from app import model, views, utils

logger = get_logger(__name__)

# route_list: List[Tuple[Blueprint, str]] = []

# def fetch_route(blueprint: Blueprint, prefix: str):
#     t: Tuple[Blueprint, str] = (blueprint, prefix)
#     route_list.append(t)

# def regist_blueprint(app: Flask, src_dir: str):
#     app_dir = path.join(config.root_dir, src_dir)
#     for routes in listdir(app_dir):
#         route_path: str = path.join(app_dir, routes)
#         if (not path.isfile(route_path)) \
#                 and routes != 'static' \
#                 and routes != 'templates' \
#                 and not routes.startswith('__'):
#             __import__('app.' + routes)
    
#     for blueprint in route_list:
#         app.register_blueprint(blueprint[0], url_prefix=blueprint[1])


def create_app(env: str="production") -> Flask:
    print("launch env context: %s" % env)
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    config_obj: Any = config.configInfo[env]
    logger.debug(config_obj.SQLALCHEMY_DATABASE_URI)
    logger.debug(config_obj.REDIS_URI)
    app.config.from_object(config_obj)
    config_obj.init_app(app)
    # 插件注册
    model.init_app(app, env)
    views.init_app(app)
    utils.init_app(app)
    # regist_blueprint(app, '')
    # 更新 celery 配置
    celery_app.conf.update(app.config)
    cold_data.prepare(app)
    return app
