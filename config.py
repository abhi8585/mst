# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# SQLALCHEMY_DATABASE_URI = 'mysql://admin:Romil123@mondelez.c3uhktkf90fd.ap-south-1.rds.amazonaws.com:3306/mts'

import os
from   decouple import config

class Config(object):

    basedir    = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_007')

    # Limit the posts to show pagination
    POSTS_PER_PAGE = 10

    # AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='minioadmin')
    # AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='minioadmin')
    # AWS_BUCKET_NAME = config('AWS_BUCKET_NAME')
    # AWS_ENDPOINT_URL = config('AWS_ENDPOINT_URL',default='http://127.0.0.1:9000')

    # # Mail Config
    MAIL_SERVER = config('MAIL_SERVER', default='smtpout.secureserver.net')
    MAIL_PORT   = config('MAIL_PORT', default=465)
    MAIL_USE_SSL = config('MAIL_USE_SSL', default=True)
    MAIL_USE_TLS = config('MAIL_USE_TLS', default=False)
    MAIL_USERNAME = config('MAIL_USERNAME',default='admin@mondeleztnt.in')
    MAIL_PASSWORD = config('MAIL_PASSWORD', default='@admin123')
    MAIL_DEFAULT_SENDER = config('MAIL_DEFAULT_SENDER', default= os.environ.get('MAIL_DEFAULT_SENDER','admin@mondeleztnt.in') )
    # This will create a file in <app> FOLDER
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:''@localhost/mts'
    SQLALCHEMY_DATABASE_URI = 'mysql://admin:Romil123@mondelez.c3uhktkf90fd.ap-south-1.rds.amazonaws.com:3306/mts'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY  = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # AWS S3 Bucket Config
    # AWS_ACCESS_KEY_ID = 'minioadmin'
    # AWS_SECRET_ACCESS_KEY = 'minioadmin'
    # AWS_BUCKET_NAME = 'dp-bucket'
    # AWS_ENDPOINT_URL = None

  
    
    # PostgreSQL database
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:''@localhost/mts'
    SQLALCHEMY_DATABASE_URI = 'mysql://admin:Romil123@mondelez.c3uh/ktkf90fd.ap-south-1.rds.amazonaws.com:3306/mts'
#
class DebugConfig(Config):
    DEBUG = True
    FLASK_DEBUG=True

# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
