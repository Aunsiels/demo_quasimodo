import os
from logging.config import fileConfig

from flask import Flask, request
from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate(db)

from quasimodo_website.config import Config
from quasimodo_website.homepage import bp as bp_homepage
from quasimodo_website.explorer import bp as bp_explorer
from quasimodo_website.models import create_all_db


def create_app(testing=False):
    if not testing:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        fileConfig(os.path.abspath(os.path.dirname(__file__)) + '/logging.cfg')
    app = Flask(__name__)
    app.config.from_object(Config)
    Bootstrap(app)
    FontAwesome(app)
    app.config["TESTING"] = testing
    app.register_blueprint(bp_homepage)
    app.register_blueprint(bp_explorer, url_prefix='/explorer')
    db.init_app(app)
    with app.app_context():
        create_all_db()

    @app.before_request
    def log_the_request():
        app.logger.info(request)

    return app
