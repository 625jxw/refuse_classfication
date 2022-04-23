import os


class Config:
    DEBUG = True
    # mysql+pymysql://user:password@hostip:port/databasename
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:shenao20010712@localhost:3306/name'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SECRET_KEY = 'asdawasd'
    # 项目路径
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # 静态文件夹的路径
    STATIC_DIR = os.path.join(BASE_DIR,'static')
    TEMPLATE_DIR = os.path.join(BASE_DIR,'templates')
    # 头像的上传目录
    UPLOAD_ICON_DIR = os.path.join(STATIC_DIR,'upload\icon')
    # 相册的上传目录
    UPLOAD_PHOTO_DIR = os.path.join(STATIC_DIR,'upload\photo')


class DevelopmentConfig(Config):
    ENV = 'development'


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False












