from flask import Flask
from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate(db)

from demo.config import Config
from demo.homepage import bp as bp_homepage
from demo.explorer import bp as bp_explorer
from demo.models import create_all_db


def create_app(testing=False):
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
    return app
