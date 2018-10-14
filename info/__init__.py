import logging
from logging.handlers import RotatingFileHandler

from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from config import config_dict
import redis
from flask_session import Session
from flask_wtf import CSRFProtect

# 定义redis_store
redis_store = None

# 定义db
db = SQLAlchemy()
def create_app(config_name):

    app = Flask(__name__)

    # 根据传入的配置名称，获取对应的配置类
    config = config_dict.get(config_name)

    # 记录日志信息的方法
    log_file(config.LEVEL)

    # 加载配置类信息
    app.config.from_object(config)

    # 创建SQLALCHEMY对象，管理app
    # db = SQLAlchemy(app)
    db.init_app(app)


    # 创建redis对象
    global redis_store
    redis_store = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

    # 初始化Session,读取app身上session的配置信息
    Session(app)

    # 保护app，使用CSRFProtect
    CSRFProtect(app)

    #注册首页蓝图index_blue,到app中
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)
    print(app.url_map)

    return app

# 记录日志信息的方法
def log_file(LEVEL):
    # 设置日志的记录等级
    logging.basicConfig(level=logging.DEBUG)  # 调试debug级DEBUG<INFO<WARNING<ERROR
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)