import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery   # 异步任务
from flask_mail import Mail

app = Flask('metaboatlas', template_folder="templates", static_folder="static")
app.config.from_pyfile('settings.py')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI", default="sqlite:///")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", default="123456")
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND']='redis://localhost:6379/0'

app.config.update(
    MAIL_SERVER = os.getenv('MAIL_SERVER'),
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USERNAME = os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER = ('栾恩慧', os.getenv('MAIL_USERNAME'))
)

db = SQLAlchemy(app)
mail = Mail(app)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL']) #异步任务
celery.conf.update(app.config)

from metaboatlas.blueprints.auth import auth_bp
from metaboatlas.blueprints.api import api_bp
from metaboatlas.blueprints.html import html_bp

app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(html_bp, url_prefix="/")
app.register_blueprint(auth_bp, url_prefix="/auth")

from metaboatlas import models, views, commands