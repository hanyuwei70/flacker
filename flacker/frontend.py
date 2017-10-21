# -*- coding: utf-8 -*-
"""
    flacker.frontend
    ~~~~~~~~~~~~~~~~

    A BitTorrent tracker written in Python with Flask.

    :copyright: 2012 by Christoph Heer <Christoph.Heer@googlemail.com
    :license: BSD, see LICENSE for more details.
"""

from flask import Blueprint, render_template, request, abort, flash, redirect, url_for, jsonify, make_response
from flask_login import login_required
from bencode import bencode, bdecode
from hashlib import sha1

from .tracker import get_torrent_list
from werkzeug.utils import secure_filename
from .redisdata import redis

import traceback
from datetime import datetime

frontend = Blueprint("frontend", "flacker.frontend")
UPLOAD_FLODER = 'torrents'


@frontend.route('/')
@login_required
def index():
    return render_template("index.html", torrents=get_torrent_list())


def read_torrent_file(torrent_file_path):
    with open(torrent_file_path, 'rb') as f:
        info_dict = bdecode(f.read())['info']
        info_hash = sha1(bencode(info_dict)).hexdigest()
    return info_hash, info_dict


def exist_torrent(info_hash):
    return redis.sismember('torrents', info_hash)


@frontend.route('/torrent', methods=['GET', 'POST'])
@frontend.route('/torrent/<info_hash>', methods=['DELETE'])
@login_required
def torrent(info_hash=None):
    """
    创建/删除种子
    所有表单中 info_hash 和 name 均为必填
    :return:
    """

    class ArgsError(Exception):
        pass

    class TorrentDuplicate(Exception):
        pass

    if request.method == 'GET':
        return render_template('torrent.html')
    elif request.method == 'POST':
        conntype = ""
        try:
            info_hash = ""
            name = ""
            try:
                if request.headers['content-type'] == 'application/x-www-form-urlencoded':
                    # web方式提交info_hash或文件
                    # 文件直接用js处理完毕然后提交info_hash和name
                    conntype = "web"
                    info_hash = request.form['info_hash']
                    name = request.form['name']
                elif request.headers['content-type'] == 'application/json':
                    # API方式提交info_hash
                    conntype = "json"
                    res = request.get_json()
                    info_hash = res['info_hash']
                    name = res['name']
            except KeyError:
                raise ArgsError
            import re
            info_hash = info_hash.lower()
            if len(info_hash) is not 40:
                raise ArgsError
            if bool(re.compile(r'[^a-f0-9.]').search(info_hash)):
                raise ArgsError
            if exist_torrent(info_hash):
                raise TorrentDuplicate
            redis.sadd('torrents', info_hash)
            tkey = 'torrent:%s' % info_hash
            redis.hset(tkey, 'name', name)
            redis.hset(tkey, 'added', datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
            redis.hset(tkey, 'downloaded', 0)
            if conntype is "web":
                flash("创建成功")
                return redirect(url_for("frontend.index"))
            elif conntype is "json":
                return make_response(jsonify({"message": "torrent created"}), 201)
            else:
                raise RuntimeError
        except ArgsError:
            if conntype is "web":
                flash('参数错误')
                return redirect(url_for('frontend.torrent'))
            elif conntype is "json":
                return make_response(jsonify({'error': "missing args"}), 400)
            else:
                raise RuntimeError
        except TorrentDuplicate:
            if conntype is "web":
                flash("此种子已添加")
                return redirect(url_for('frontend.torrent'))
            elif conntype is "json":
                return make_response(jsonify({"error": "This torrent exists"}), 409)
            else:
                raise RuntimeError
    elif request.method == 'DELETE':
        abort(501)
    else:
        abort(400)
