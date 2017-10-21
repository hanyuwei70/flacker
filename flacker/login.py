# -*- coding:utf-8 -*-

from flask import Blueprint, request, render_template, current_app, redirect, abort, url_for, jsonify
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user
from hashlib import pbkdf2_hmac
import secrets
from .redisdata import redis

from .const import Auth

auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static')
login_manager = LoginManager()


class User(UserMixin):
    def __init__(self, username):
        self.username = username

    def get_id(self):
        return self.username


def _check_password(username, password):
    salt = current_app.config['LOGIN_SALT']
    hashed = pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100)
    res = redis.hget(f'user:{username}', 'password')
    return res == hashed


def _set_password(username, password):
    """
    :param str username: 用户名
    :param str password: 密码
    """
    salt = current_app.config['LOGIN_SALT']
    assert isinstance(salt, str)
    hashed = pbkdf2_hmac('sha256', password.encode(), salt, 100)
    redis.hset(f'user:{username}', 'password', hashed)


def _add_user(username, password):
    print(type(redis))
    redis.sadd('users', username)
    redis.hset(f'user:{username}', 'password', None)
    _set_password(username, password)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    class NotMatch(Exception):
        pass

    WEB = 1
    API = 2
    username = None
    password = None
    conntype = None
    try:
        if request.method == 'GET':
            return render_template('login.html')
        try:
            if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':  # login from webpage
                conntype = WEB
                print(request.form)
                username = request.form['username']
                password = request.form['password']
                nexturl = request.args.get('next')
            elif request.headers['Content-Type'] == 'application/json':  # login from API
                d = request.get_json()
                conntype = API
                username = d['username']
                password = request.form['password']
        except KeyError:
            abort(400)
        assert isinstance(username, str)
        assert isinstance(password, str)
        assert conntype in (WEB, API)
        if _check_password(username, password):
            user = User(username)
            login_user(user)
            if conntype is WEB:
                return redirect(url_for('frontend.index'))
            elif conntype is API:
                # TODO:give a token
                token = secrets.token_hex()
                redis.set(f'token:{token}', username)
                redis.expire(f'token:{token}', Auth.DEFAULT_EXPIRE_SEC)
                return jsonify({"success": True, "token": token, "expire": Auth.DEFAULT_EXPIRE_SEC})
        else:
            raise NotMatch
    except NotMatch:
        if conntype is WEB:
            return render_template('login.html', error={"errno": Auth.PASSWORDMISMATCH})
        elif conntype is API:
            return jsonify({"errno": Auth.PASSWORDMISMATCH})
        pass


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("https://www.vcb-s.com")


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@login_manager.request_loader
def load_user_from_request(request):
    if 'content-type' not in request.headers or request.headers['content-type'] != 'application/json':
        return None
    req=request.get_json()
    username=redis.get(f"token:{req['token']}")
    return None if username is None else User(username)

@login_manager.unauthorized_handler
def unauthorized():
    if request.method=='GET':
        return redirect(url_for('auth.login'))
