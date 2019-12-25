import os
import logging

root_dir = os.path.abspath((os.path.dirname(__file__)))

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI", "mysql+pymysql://root:12345678@localhost:3306/sky_main"
)

REDIS_URI = os.environ.get('REDIS_URI', 'redis://localhost:6379/')
class Config:
    # 开启跨站请求伪造防护
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24)
    """SQLALCHEMY配置"""
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    """配置上传文件相关"""

    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), "disk"))
    # UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = ("txt", "png", "jpg", "jpeg")

    """Flask Uploads 配置"""
    UPLOADED_PHOTOS_DEST = UPLOAD_FOLDER
    UPLOADS_DEFAULT_DEST = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    """Flask Security 配置"""
    SECURITY_PASSWORD_SALT = "saltValue"
    SECURITY_PASSWORD_HASH = "sha512_crypt"

    """ Logging 设置 """
    LOGGING_FORMATTER = (
        "%(levelname)s - %(asctime)s - process: %(process)d - %(filename)s - %(name)s - %(lineno)d - %(module)s - %(message)s"
    ) # 每条日志输出格式
    LOGGING_DATE_FORMATTER = "%a %d %b %Y %H:%M:%S"
    LOGGING_DIR = os.path.join(root_dir, "logs")
    LOG_LEVEL = "DEBUG"  # 日志输出等级
    LOG_ENABLE = True  # 是否开启日志

    """Celery 配置"""
    from datetime import timedelta
    CELERY_RESULT_BACKEND = REDIS_URI

    BROKER_URL = REDIS_URI + '0'

    CELERY_TIMEZONE='Asia/Shanghai'

    CELERY_TASK_SERIALIZER = 'json'

    CELERY_RESULT_SERIALIZER = 'json'

    CELERY_ACCEPT_CONTENT=['json']

    # 定义定时任务
    CELERYBEAT_SCHEDULE = {
        'app.task.beat.parse_rsses': {
            'task': 'app.task.beat.parse_rsses',
            'schedule': timedelta(seconds=60*60*4),
            'args': ()
        }
    }
    
    @classmethod
    def init_app(app, *args, **kwargs):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SERVICE_TOKEN_SUFFIX = "im_token_suffix"
    # 打开数据库语句输出
    SQLALCHEMY_ECHO = False
    # 分页数量
    PAGE_LIMIT = 11


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL"
    ) or "sqlite:///" + os.path.join(root_dir, "data-test.sqlite")
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False


configInfo = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
