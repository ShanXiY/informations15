from flask import abort
from flask import current_app, jsonify
from flask import g
from flask import json
from flask import request

from info import db
from info.models import News, Comment, CommentLike, User
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import news_blue
from flask import render_template

# 功能描述：关注&取消关注
# 请求路径：/news/followed_user
# 请求方式：POST
# 请求参数：user_id,action
# 返回值：errno，errmsg
@news_blue.route('/followed_user', methods=['POST'])
@user_login_data
def followed_user():
    """
    1.判断用户是否登陆
    2.获取参数
    3.校验参数，为空校验
    4.判断操作类型
    5.根据作者编号取出作者对象，判断作者对象是否存在
    6.根据操作类型，关注&取消关注
    7.返回响应
    :return:
    """


    # 1.判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.NODATA,errmsg="用户未登录")

    # 2.获取参数
    user_id = request.json.get("user_id")
    action = request.json.get("action")

    # 3.校验参数，为空校验
    if not all([user_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 4.判断操作类型
    if not action in ["follow","unfollow"]:
        return jsonify(errno=RET.DATAERR,errmsg="操作类型有误")

    # 5.根据作者编号取出作者对象，判断作者对象是否存在
    try:
        author = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取用户失败")

    if not author:
        return jsonify(errno=RET.NODATA,errmsg="用户不存在")



    try:
        # 6.根据操作类型，关注&取消关注
        if action == "follow":
            # 判断用户是否已经关注过该作者了
            if not g.user in author.followers:
                author.followers.append(g.user)
        else:
            # 判断用户是否已经关注过该作者了
            if g.user in author.followers:
                author.followers.remove(g.user)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作异常")

    # 7.返回响应


    return jsonify(errno=RET.OK, errmsg="操作成功")



# 功能描述：点赞
# 请求路径：/news/comment_like
# 请求方式：POST
# 请求参数：news_id,comment_id,action,g.user
# 返回值：errno，errmsg
@news_blue.route('/comment_like', methods=['POST'])
@user_login_data
def comment_like():
    """
    - 1.判断用户是否登陆
    - 2.获取参数
    - 3.校验参数,为空校验
    - 4.校验操作类型
    - 5.通过评论编号,取出评论对象
    - 6.判断评论对象是否存在
    - 7.根据操作类型,点赞,或者取消点赞
    - 8.返回响应
    :return:
    """

    # - 1.判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.NODATA,errmsg="用户未登录")

    # - 2.获取参数
    comment_id = request.json.get("comment_id")
    action = request.json.get("action")

    # - 3.校验参数,为空校验
    if not all([comment_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # - 4.校验操作类型
    if not action in ["add","remove"]:
        return jsonify(errno=RET.DATAERR,errmsg="操作类型有误")

    # - 5.通过评论编号,取出评论对象
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="评论获取失败")

    # - 6.判断评论对象是否存在
    if not comment:
        return jsonify(errno=RET.NODATA,errmsg="评论不存在")

    # - 7.根据操作类型,点赞,或者取消点赞
    try:
        if action == "add":
            # 判断用户是否点过赞
            comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id,
                                                    CommentLike.user_id == g.user.id).first()
            if not comment_like:
                # 判断点赞对象，设置属性
                comment_like = CommentLike()
                comment_like.comment_id = comment_id
                comment_like.user_id = g.user.id

                # 添加到数据库
                db.session.add(comment_like)
                db.session.commit()

                # 更新评论的点赞的数量
                comment.like_count += 1
        else:
            # 判断用户是否点过赞
            comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id,
                                                    CommentLike.user_id == g.user.id).first()
            if comment_like:
                # 移除点赞对象
                db.session.delete(comment_like)

                # 更新评论的点赞的数量
                if comment.like_count > 0:
                    comment.like_count -= 1
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="操作失败")

    # - 8.返回响应
    return jsonify(errno=RET.OK,errmsg="操作成功")

# 功能描述：评论
# 请求路径：/news/news_comment
# 请求方式：POST
# 请求参数：news_id,comment,parent_id,g.user
# 返回值:errno,errmsg,评论字典
@news_blue.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    """
    1.判断用户是否登陆
    2.获取参数
    3.校验参数，为空校验
    4.根据新闻编号，取出新闻对象
    5.判断新闻对象是否存在
    6.创建评论对象，设置属性
    7.保存到数据库
    8.返回响应
    :return:
    """

    # 1.判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.NODATA,errmsg="用户未登陆")

    # 2.获取参数
    news_id = request.json.get("news_id")
    content = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    # 3.校验参数，为空校验
    if not all([news_id,content]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 4.根据新闻编号，取出新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")

    # 5.判断新闻对象是否存在
    if not news: return jsonify(errno=RET.NODATA,errmsg="新闻不存在")

    # 6.创建评论对象，设置属性
    comment = Comment()
    comment.user_id = g.user.id
    comment.news_id = news_id
    comment.content = content

    if parent_id:
        comment.parent_id = parent_id

    # 7.保存到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="评论失败")

    # 8.返回响应
    return jsonify(errno=RET.OK,errmsg="评论成功",data=comment.to_dict())


#功能描述：收藏/取消收藏
# 请求路径：/news/news_collect
# 请求方式：POST
# 请求参数：news_id,action,g.user
# 返回值：errno,errmsg
@news_blue.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    """
    1.判断用户是否登陆
    2.获取参数
    3.校验参数，为空校验
    4.判断操作类型
    5.判断新闻编号取出新闻对象
    6.根据新闻对象是否存在
    7.根据操作类型，收藏或者取消收藏操作
    8.返回响应
    :return:
    """

    # 1.判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.DBERR,errmsg="用户未登录")

    # 2.获取参数
    json_data = request.data
    dict_data = json.loads(json_data)
    news_id = dict_data.get("news_id")
    action = dict_data.get("action")

    # 3.校验参数，为空校验
    if not all([news_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")


    # 4.判断操作类型
    if not action in ["collect","cancel_collect"]:
        return jsonify(errno=RET.DATAERR,errmsg="操作类型有误")

    # 5.判断新闻编号取出新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")

    # 6.根据新闻对象是否存在
    if not news: return jsonify(errno=RET.NODATA,errmsg="新闻不存在")

    # 7.根据操作类型，收藏或者取消收藏操作
    try:
        if action == "collect":
            # 判断是否收藏过该新闻
            if not news in g.user.collection_news:
                g.user.collection_news.append(news)
        else:
            if news in g.user.collection_news:
                g.user.collection_news.remove(news)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="操作失败")



    # 8.返回响应
    return jsonify(errno=RET.OK,errmsg="操作成功")


# 功能描述：获取新闻详情信息
# 请求路径：/news/<int：news_id>
# 请求方式：GET
# 请求参数：news_id
# 返回值：detail.html页面，用户data字典数据
@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    # 根据传入的新闻编号，获取新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="新闻获取失败")

    # 判断新闻是否存在
    if not news:
        abort(404)

    # 查询热门新闻数据
    try:
        news_cli = News.query.order_by(News.clicks.desc()).limit(6).all()
    except Exception as e:
        current_app.logger.error(e)

    # 将新闻列表转成字典列表
    click_news_list = []
    for news_content in news_cli:
        click_news_list.append(news_content.to_dict())

        # 获取用户数据
        # 获取用户的编号,从session
        # user_id = session.get("user_id")
        #
        # #判断用户是否存在
        # user = None
        # if user_id:
        #     try:
        #         user = User.query.get(user_id)
        #     except Exception as e:
        #         current_app.logger.error(e)

    # 判断用户是否收藏过
    is_collected = False
    if g.user and news in g.user.collection_news:
        is_collected = True

    # 查询所有的评论
    try:
        comments =Comment.query.filter(Comment.news_id == news.id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取评论失败")

    try:
        # 获取用户所有点赞过的评论编号
        comment_likes = []
        if g.user:
            comment_likes = g.user.comment_likes

        comment_ids = []
        for comment_like in comment_likes:
            comment_ids.append(comment_like.comment_id)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取点赞数据失败")

    # 将评论对象列表转成字典列表
    comments_list = []
    for comment in comments:
        com_dict = comment.to_dict()
        com_dict["is_like"] = False

        # 判断当前用户有对该评论点过赞
        if g.user and comment.id in comment_ids:
            com_dict["is_like"] = True

        comments_list.append(com_dict)

    # 判断当前用户是否有关注当前新闻的作者
    is_followed = False
    if g.user and news.user:
        if g.user in news.user.followers:
            is_followed = True


    # 携带数据渲染页面
    data ={
        "news":news.to_dict(),
        "click_news_list":click_news_list,
        "user_info": g.user.to_dict() if g.user else "",
        "is_collected":is_collected,
        "comments":comments_list,
        "is_followed":is_followed
    }

    return render_template("news/detail.html",data=data)