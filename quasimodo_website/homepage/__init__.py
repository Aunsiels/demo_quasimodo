from flask import Blueprint

bp = Blueprint('homepage', __name__)

from quasimodo_website.homepage import routes
