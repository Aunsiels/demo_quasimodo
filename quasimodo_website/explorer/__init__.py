from flask import Blueprint

bp = Blueprint('explorer', __name__)

from quasimodo_website.explorer import routes
