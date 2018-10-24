from flask import Blueprint

# 创建蓝图
from flask import redirect
from flask import request
from flask import session

admin_blue = Blueprint("admin",__name__,url_prefix="/admin")

from . import views


# 只要访问了管理员的视图，需要做蓝图，判断当前用户是否是管理员
#如果访问管理员登陆页面不需要做拦截，因为需要输入管理员密码
#如果访问管理员其他页面需要做拦截
@admin_blue.before_request
def visit_admin():
    # 访问不是管理员登陆页面，需要拦截
    if not request.url.endswith("/admin/login"):
        #不是管理员用户，需要做拦截
        if not session.get("is_admin"):
            # print(request.url)
            # print("----------")
            return redirect("/")