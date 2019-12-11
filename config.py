import os
import logging

root_dir = os.path.abspath((os.path.dirname(__file__)))

SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'mysql+pymysql://root:12345678@mysql:3000/sky_main')

class Config:
    # 开启跨站请求伪造防护
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    """SQLALCHEMY配置"""
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


    """配置上传文件相关"""
    
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), "..", "disk"))
    # UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = ('txt', 'png', 'jpg', 'jpeg')

    """Flask Uploads 配置"""
    UPLOADED_PHOTOS_DEST = UPLOAD_FOLDER
    UPLOADS_DEFAULT_DEST = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = 10*1024*1024

    """Flask Security 配置"""
    SECURITY_PASSWORD_SALT = "saltValue"
    SECURITY_PASSWORD_HASH = "sha512_crypt"


    """ Logging 设置 """
    LOGGING_FORMATTER = "%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s"
    LOGGING_DATE_FORMATTER = "%a %d %b %Y %H:%M:%S"
    LOGGING_DIR = os.path.join(root_dir, 'logs')

    @classmethod
    def init_app(app, *args, **kwargs):
        log_level_configs = {
            logging.DEBUG: 'debug.log',
            logging.ERROR: 'error.log'
            }
        for level, file_name in log_level_configs.items():
            level:str = logging.getLevelName(level)
            filename=os.path.join(Config.LOGGING_DIR, file_name)
            if not os.path.exists(Config.LOGGING_DIR):
                os.makedirs(Config.LOGGING_DIR)

            if not os.path.exists(filename):
                open(filename, 'w').close()
            
            logging.basicConfig(
                filename=filename, 
                level=level
                )

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SERVICE_TOKEN_SUFFIX = 'im_token_suffix'
    # 打开数据库语句输出
    SQLALCHEMY_ECHO = True
    # 分页数量
    PAGE_LIMIT = 11

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(root_dir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False

configInfo = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}