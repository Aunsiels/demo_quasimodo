from flask import Blueprint

bp = Blueprint('explorer', __name__)

from demo.explorer import routes
