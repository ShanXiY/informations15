"""
项目启动配置
1.数据库配置
2.redis配置
3.session配置，为后续登陆保持做铺垫
4.日志文件配置
5.CSRFProtect配置，为了对‘POST’，‘PUT’，‘DISPATCH’，‘DELETE’做保护
6.迁移配置
"""
import logging
import random
from datetime import datetime, timedelta

from flask import Flask,session,current_app, jsonify
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app,db,models
#需要知道有models这个文件存在即可


# 传入标记，加载对应的配置环境信息
from info.models import User
from info.utils.response_code import RET

app = create_app("develop")

# 创建manager对象，管理app
manager = Manager(app)

# 关联db，app，使用Migrate
Migrate(app,db)

# 给manager添加操作命令
manager.add_command("db",MigrateCommand)

# 创建管理方法
# 加上@manager.option()之后就可以通过命令行的方法调用程序
# 参数1：表示参数的名称，参数2：表示参数名称描述信息，参数3：表示用来传递到方法的形式参数中
@manager.option('-p', '--password', dest='password')
@manager.option('-u', '--username', dest='username')
def create_admin(username,password):
    # 1.创建管理员对象
    admin = User()

    # 2.设置属性
    admin.nick_name = username
    admin.mobile = username
    admin.password = password
    admin.is_admin = True

    # 3,保存到数据库
    try:
        db.session.add(admin)
        db.session.commit
    except Exception as e:
        current_app.logger.error(e)
        return "创建失败"

    return "创建成功"


# 添加测试用户
@manager.option('-t', '--test', dest='test')
def add_test_user(test):
    #定义用户容器
    user_list = []

    #for循环创建1000个用户
    for i in range(0,1001):
        #创建用户对象，设置属性
        user = User()
        user.nick_name = "王守%d"%i
        user.mobile = "1335%07d"%i
        user.password_hash = "pbkdf2:sha256:50000$dk2SPnVJ$a8b17e626e8121d14969cbe6ed06850448daed8902173000ae4809b9b99b94e0"

        #设置用户近31天的登陆时间
        user.last_login = datetime.now() -timedelta(seconds=random.randint(0,3600*24*31))

        #添加到容器中
        user_list.append(user)

        #添加到数据库中
        try:
            db.session.add_all(user_list)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return "添加失败"

    return "添加成功"


if __name__ == '__main__':
    manager.run()