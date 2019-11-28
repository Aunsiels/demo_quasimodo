from flask import Flask
from demo.homepage import bp as bp_homepage


def create_app(testing=False):
    app = Flask(__name__)
    app.config["TESTING"] = testing
    app.register_blueprint(bp_homepage)
    return app