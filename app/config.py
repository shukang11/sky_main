import os
import logging

root_dir = os.path.abspath((os.path.dirname(__file__)))

class ConfigBase:
    # 开启跨站请求伪造防护
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24)
    """SQLALCHEMY配置"""
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "mysql+pymysql://root:12345678@mysql:3306/sky_main")

    REDIS_URI = os.environ.get("REDIS_URI", "redis://redis:6379/")

    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    """Flask Email 配置"""
    MAIL_DEBUG = False             # 开启debug，便于调试看信息
    MAIL_SUPPRESS_SEND = False    # 发送邮件，为True则不发送
    MAIL_SUBJECT_PREFIX = 'SKY_MAIL' # 邮件的前缀
    MAIL_SERVER = os.environ.get("MAIL_SERVER") # 邮箱的地址
    MAIL_PORT = os.environ.get("MAIL_PORT") # 端口
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL") # 是否使用ssl
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") # 是否使用tls
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME") # 用户名，邮箱
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") # 密码，授权码
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER") # 默认的发送者


    """配置上传文件相关"""
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), "disk"))
    # UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = set(["txt", "pdf", "png", "jpg", "jpeg", "gif"])

    """Flask Uploads 配置"""
    UPLOADED_PHOTOS_DEST = UPLOAD_FOLDER
    UPLOADS_DEFAULT_DEST = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    """Flask Security 配置"""
    SECURITY_PASSWORD_SALT = "saltValue"
    SECURITY_PASSWORD_HASH = "sha512_crypt"

    """ Logging 设置 """
    LOGGING_FORMATTER = "%(levelname)s - %(asctime)s - process: %(process)d - %(filename)s - %(name)s - %(lineno)d - %(module)s - %(message)s"  # 每条日志输出格式
    LOGGING_DATE_FORMATTER = "%a %d %b %Y %H:%M:%S"
    LOGGING_DIR = os.path.join(root_dir, "logs")
    LOG_LEVEL = "DEBUG"  # 日志输出等级
    LOG_ENABLE = True  # 是否开启日志

    """Celery 配置"""
    from datetime import timedelta

    CELERY_RESULT_BACKEND = REDIS_URI

    BROKER_URL = REDIS_URI + "0"

    CELERY_TIMEZONE = "Asia/Shanghai"

    CELERY_TASK_SERIALIZER = "json"

    CELERY_RESULT_SERIALIZER = "json"

    CELERY_ACCEPT_CONTENT = ["json"]

    # 定义定时任务
    CELERYBEAT_SCHEDULE = {
        "app.task.beat.parse_rsses": {
            "task": "app.task.beat.parse_rsses",
            "schedule": timedelta(seconds=60*60*4),
            "args": (),
        },
        "app.task.beat.report_rss_content": {
            "task": "app.task.beat.report_rss_content",
            "schedule": timedelta(seconds=60),
            "args": (),
        }
    }
    @classmethod
    def init_app(cls, app, *args, **kwargs):
        pass


class DevelopmentConfig(ConfigBase):
    # 开启跨站请求伪造防护
    SECRET_KEY = os.urandom(24)
    """SQLALCHEMY配置"""
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URI", "mysql+pymysql://root:12345678@localhost:3306/sky_main")

    REDIS_URI = os.environ.get("DEV_REDIS_URI", "redis://localhost:6379/")

    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    
    """Flask Email 配置"""
    MAIL_DEBUG = True             # 开启debug，便于调试看信息
    MAIL_SUPPRESS_SEND = False    # 发送邮件，为True则不发送
    MAIL_SUBJECT_PREFIX = 'SKY_MAIL' # 邮件的前缀
    MAIL_SERVER = os.environ.get("MAIL_SERVER") # 邮箱的地址
    MAIL_PORT = os.environ.get("MAIL_PORT") # 端口
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL") # 是否使用ssl
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") # 是否使用tls
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME") # 用户名，邮箱
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") # 密码，授权码
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER") # 默认的发送者

    """Celery 配置"""
    from datetime import timedelta

    CELERY_RESULT_BACKEND = REDIS_URI

    BROKER_URL = REDIS_URI + "0"

    # 定义定时任务
    CELERYBEAT_SCHEDULE = {
        "app.task.beat.report_rss_content": {
            "task": "app.task.beat.report_rss_content",
            "schedule": timedelta(seconds=60),
            "args": (),
        }
    }
    @classmethod
    def init_app(cls, app, *args, **kwargs):
        pass

class TestingConfig(ConfigBase):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URI", "mysql+pymysql://root:12345678@localhost:3306/sky_main")

    REDIS_URI = os.environ.get("TEST_REDIS_URI", "redis://localhost:6379/")

    """Celery 配置"""
    from datetime import timedelta

    CELERY_RESULT_BACKEND = REDIS_URI

    BROKER_URL = REDIS_URI + "0"
    
    WTF_CSRF_ENABLED = False


class ProductionConfig(ConfigBase):
    DEBUG = False


configInfo = {
    "develop": DevelopmentConfig,
    "testing": TestingConfig,
    "product": ProductionConfig,
    "default": DevelopmentConfig,
}
