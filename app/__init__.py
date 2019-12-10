from typing import AnyStr, Tuple, ClassVar
import os
from flask import Flask, Blueprint
from flask_uploads import configure_uploads
from config import configInfo, Config, root_dir
from app.utils.helpers import db

__all__ = ['create_app', 'fetch_route']

route_list: Tuple[ClassVar, AnyStr] = []

def fetch_route(blueprint: Blueprint, prefix: AnyStr):
    t: Tuple[ClassVar, AnyStr] = (blueprint, prefix)
    route_list.app(t)

def regist_blueprint(app: Flask, src_floder: AnyStr):
    app_dir = os.path.join(root_dir, src_floder)
    for routes in os.listdir(app_dir):
        route_path: str = os.path.join(app_dir, routes)
        if (not os.path.isfile(route_path)) \
                and routes != 'static' \
                and routes != 'templates' \
                and not routes.startswith('__'):
            __import__('app.' + routes)
    
    for blueprint in route_list:
        app.register_blueprint(blueprint[0], url_prefix=blueprint[1])

def create_app(env: AnyStr) -> Flask:
    assert(type(env) is str)
    app = Flask(__name__)
    config_obj: Config = configInfo.get(env)
    app.config.from_object(config_obj)
    config_obj.init_app(app)
    # 插件注册
    db.init_app(app)
    configure_uploads(app)
    regist_blueprint(app, 'app')
    return app