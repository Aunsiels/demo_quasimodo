import logging
import os
from logging.config import fileConfig

import rq
from flask import Flask, request
from flask.logging import create_logger
from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome
from flask_session import Session
from redis import Redis

from quasimodo_website.utils import get_ip
from quasimodo_website.database import DB
from quasimodo_website.config import Config
from quasimodo_website.homepage.blueprint import BP as BP_HOMEPAGE
from quasimodo_website.explorer.blueprint import BP as BP_EXPLORER
from quasimodo_website.taboo.blueprint import BP as BP_TABOO
from quasimodo_website.tasks.blueprint import BP as BP_TASKS
from quasimodo_website.models import create_all_db


def create_app(testing=False):
    if not testing:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        fileConfig(os.path.abspath(os.path.dirname(__file__)) + '/logging.cfg')
    app = Flask(__name__)
    app.config.from_object(Config)
    Bootstrap(app)
    Session(app)
    FontAwesome(app)
    app.config["TESTING"] = testing
    app.register_blueprint(BP_HOMEPAGE)
    app.register_blueprint(BP_EXPLORER, url_prefix='/explorer')
    app.register_blueprint(BP_TABOO, url_prefix='/taboo')
    app.register_blueprint(BP_TASKS, url_prefix='/tasks')
    logger = create_logger(app)
    if testing:
        logger.setLevel(logging.DEBUG)
    DB.init_app(app)
    with app.app_context():
        create_all_db()
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('quasimodo-tasks', connection=app.redis, default_timeout=50000)

    @app.before_request
    # pylint: disable=unused-variable
    def log_the_request():
        if not app.config["TESTING"]:
            logger.info("\t".join([get_ip(),
                                   request.url,
                                   str(request.data)
                                   ]))

    return app
