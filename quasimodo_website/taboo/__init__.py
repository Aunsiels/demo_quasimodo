from flask import Blueprint

bp = Blueprint('taboo', __name__)

from quasimodo_website.taboo import routes
