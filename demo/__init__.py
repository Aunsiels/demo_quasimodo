from flask import Flask
from flask_bootstrap import Bootstrap

from demo.homepage import bp as bp_homepage


def create_app(testing=False):
    app = Flask(__name__)
    Bootstrap(app)
    app.config["TESTING"] = testing
    app.register_blueprint(bp_homepage)
    return app