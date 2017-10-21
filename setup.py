# -*- coding: utf-8 -*-
# flacker
# Copyright: (c) 2012 Christoph Heer
# License: BSD


from setuptools import setup
import sys

setup(
    name='flacker',
    version='0.2',
    url='https://github.com/jarus/flacker',
    license='BSD',
    author='Christoph Heer',
    author_email='Christoph.Heer@googlemail.com',
    description='BitTorrent tracker written with Python and Flask',
    packages=['flacker'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'flacker = flacker.manage:main',
        ],
    },
    install_requires=[
        'Flask>=0.12.2',
        'Flask-Script>=2.0.6',
        'Flask-And-Redis>=0.7',
        'bencode-python3==1.0.2',
        'flask-mysql>=1.4.0',
        'flask-login>=0.4.0'
    ]
)
if sys.version_info < (3,6):
    sys.exit("Python < 3.6 is not supported")