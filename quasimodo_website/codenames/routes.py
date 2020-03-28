from flask import render_template

from quasimodo_website.codenames.blueprint import BP


@BP.route("/")
def home():
    return render_template("codenames.html")
