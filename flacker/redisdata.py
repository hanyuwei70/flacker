# -*- coding: utf-8 -*-
"""
    flacker.redis
    ~~~~~~~~~~~~~

    A BitTorrent tracker written in Python with Flask.

    :copyright: 2012 by Christoph Heer <Christoph.Heer@googlemail.com
    :license: BSD, see LICENSE for more details.
"""

from flask_redis import FlaskRedis

redis = FlaskRedis()
