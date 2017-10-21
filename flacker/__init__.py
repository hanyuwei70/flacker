# -*- coding: utf-8 -*-
"""
    flacker
    ~~~~~~~

    A BitTorrent tracker written in Python with Flask.

    :copyright: 2012 by Christoph Heer <Christoph.Heer@googlemail.com
    :license: BSD, see LICENSE for more details.
"""

import os

from flask import Flask
#from flaskext.mysql import MySQL
#import pymysql
from flask_login import LoginManager
from .redisdata import redis

from .tracker import tracker
from .frontend import frontend
from .login import auth,login_manager

try:
    VERSION = __import__('pkg_resources').get_distribution('flacker').version
except Exception as e:
    VERSION = 'unknown'


def create_app(config=None):
    app = Flask("flacker")
    if config is not None:
        app.config.from_pyfile(os.path.join(os.getcwd(), config))
    elif 'FLACKER_CONFIG' in os.environ:
        app.config.from_envvar('FLACKER_CONFIG')
    app.jinja_env.globals['flacker_version'] = VERSION

    if app.config.get('SENTRY_DSN'):
        from raven.contrib.flask import Sentry
        sentry = Sentry(app)

    redis.init_app(app)
    login_manager.init_app(app)
    # mysql=MySQL()
    # mysql.init_app(app)
    app.register_blueprint(tracker)
    app.register_blueprint(frontend)
    app.register_blueprint(auth)

    # @app.before_first_request
    # def startup():
    #     app.logger.info("Loading torrents...")
    #     try:
    #         cur = mysql.get_db().cursor()
    #         cur.execute("SELECT * FROM torrents")
    #         res=cur.fetchall()
    #         for line in res:
    #             line['info_hash']
    #     except pymysql.err.DatabaseError:
    #         app.logger.warn("MySQL load error, torrent data incomplete!")

    return app
