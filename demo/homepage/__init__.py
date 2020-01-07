from flask import Blueprint

bp = Blueprint('homepage', __name__)

from demo.homepage import routes
