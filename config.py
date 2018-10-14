import logging
import redis

# 配置信息
class Config(object):
    # 调试模式
    DEBUG = True
    SECRET_KEY = "ASDASDSAD"

    #数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost:3306/informations15"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    #session配置
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 3600 #一个小时

    #设置日志等级默认就是DEBUG
    LEVEL = logging.DEBUG

# 开发模式的配置信息
class DevelopConfig(Config):
    pass

# 生产模式(线上模式)
class ProductConfig(Config):
    # 设置正式环境配置信息
    DEBUG = False
    #日志等级
    LEVEL = logging.ERROR

# 测试模式
class TestingConfig(Config):
    TESTING = True

# 给外界提供各种配置的访问入口
config_dict = {
    "develop":DevelopConfig,
    "product":ProductConfig,
    "test":TestingConfig
}