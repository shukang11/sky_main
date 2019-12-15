from typing import AnyStr, Tuple
import os
from flask import Flask, Blueprint

from config import configInfo, Config, root_dir
from app.utils import db, configure_uploads, fileStorage
from app.utils import migrate_manager

__all__ = ['create_app', 'fetch_route']

route_list: Tuple[Blueprint, AnyStr] = []

def fetch_route(blueprint: Blueprint, prefix: AnyStr):
    t: Tuple[Blueprint, AnyStr] = (blueprint, prefix)
    route_list.append(t)

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
        print(blueprint)
        app.register_blueprint(blueprint[0], url_prefix=blueprint[1])

def create_tables(app: Flask):
    from app.model import __all__
    with app.app_context():
        db.create_all()

def create_app(env: AnyStr) -> Flask:
    assert(type(env) is str)
    app = Flask(__name__)
    config_obj: Config = configInfo.get(env)
    print(config_obj.SQLALCHEMY_DATABASE_URI)
    app.config.from_object(config_obj)
    config_obj.init_app(app)
    # 插件注册
    db.init_app(app)
    migrate_manager.init_app(app, db)
    configure_uploads(app, fileStorage)
    regist_blueprint(app, 'app')
    return app