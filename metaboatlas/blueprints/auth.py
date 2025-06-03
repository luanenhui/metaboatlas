import os
from flask import request, Blueprint, render_template
from flask import redirect, url_for

from flask_login import LoginManager, login_required, login_user, logout_user

from metaboatlas import app, db
from metaboatlas.models import User

# ---- 登录管理 ---- #
login_manager = LoginManager()
login_manager.login_view = 'auth.login'     # 未登录用户重定向
login_manager.init_app(app)

def query_userID(username):
    id = User.query.filter(User.UserName == username).with_entities(User.id).first()
    if id is not None:
        return id[0]
    else:
        return None

@login_manager.user_loader
def load_user(userid):
    if userid is not None:
        curr_user = User()
        curr_user.id = userid
        
        return curr_user

# ---- auth_bp blueprint ---- #
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET',"POST"])
def register():
    '''用户注册，登录'''
    if request.method == "GET":
        # return "success"
        return render_template("auth.html")
    
    if request.method == "POST":
        user = User(UserName=request.form.get('username'), Email=request.form.get('email'))
        user.set_password(password=request.form.get('password'))
        db.session.add(user)
        db.session.commit()
        # return "您已成功注册"
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET',"POST"])
def login():
    '''用户注册，登录'''
    if request.method == "GET":
        return render_template("auth.html")
        # return render_template("login.html")
    
    if request.method == "POST":
        username = request.form.get('usernamelogin')   # 获取用户名
        password = request.form.get('passwordlogin')   # 获取用户密码

        user = User.query.filter(User.UserName == username).first() # 从数据库中查询用户

        if user:
            if user.validate_password(password):   # 验证密码哈希值
                login_user(user)
        
        # user = User(UserName=request.form.get('username'), Password=request.form.get('password'), Tel=request.form.get('tel'), Email=request.form.get('email'))
        # db.session.add(user)
        # db.session.commit()
        return redirect(url_for('html.index'))

@auth_bp.route('/logout', methods=['GET',"POST"])
@login_required
def logout():
    '''用户注册，登录'''
    if request.method == "GET":
        return "取消登录"
        # return render_template("login.html")
    
    if request.method == "POST":
        user = User(UserName=request.form.get('username'), Password=request.form.get('password'), Tel=request.form.get('tel'), Email=request.form.get('email'))
        db.session.add(user)
        db.session.commit()
        return "您已成功注册"