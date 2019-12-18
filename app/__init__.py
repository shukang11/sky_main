from typing import Any, List, Tuple
from os import path, listdir
from flask import Flask, Blueprint

from config import configInfo, Config, root_dir
from app.utils import db, configure_uploads, fileStorage
from app.utils import migrate_manager, get_logger
from app.utils import celery_app

__all__ = ['create_app', 'fetch_route']

logger = get_logger(__name__)

route_list: List[Tuple[Blueprint, str]] = []

def fetch_route(blueprint: Blueprint, prefix: str):
    t: Tuple[Blueprint, str] = (blueprint, prefix)
    route_list.append(t)

def regist_blueprint(app: Flask, src_floder: str):
    app_dir = path.join(root_dir, src_floder)
    for routes in listdir(app_dir):
        route_path: str = path.join(app_dir, routes)
        if (not path.isfile(route_path)) \
                and routes != 'static' \
                and routes != 'templates' \
                and not routes.startswith('__'):
            __import__('app.' + routes)
    
    for blueprint in route_list:
        app.register_blueprint(blueprint[0], url_prefix=blueprint[1])

def create_tables(app: Flask):
    from app.model import __all__
    with app.app_context():
        db.create_all()

def create_app(env: str) -> Flask:
    assert(type(env) is str)
    app = Flask(__name__)
    config_obj: Any = configInfo.get(env)
    logger.debug(config_obj.SQLALCHEMY_DATABASE_URI)
    app.config.from_object(config_obj)
    config_obj.init_app(app)
    # 插件注册
    db.init_app(app)
    migrate_manager.init_app(app, db)
    create_tables(app)
    configure_uploads(app, fileStorage)
    regist_blueprint(app, 'app')
    # 更新 celery 配置
    celery_app.conf.update(app.config)
    return app
