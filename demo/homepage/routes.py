from flask import render_template

from demo.homepage import bp


@bp.route("/")
def home():
    return render_template("homepage.html")
