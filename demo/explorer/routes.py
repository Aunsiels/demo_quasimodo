import os

from flask import render_template, request, url_for
from flask import current_app as app
from sqlalchemy import desc, asc

from demo import db
from demo.explorer import bp
from demo.models.fact import Fact, read_facts, add_all_facts_to_db


@bp.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    order_str = request.args.get("order", "pd", type=str)
    if order_str == "pd":
        order = desc(Fact.plausibility)
    elif order_str == "pa":
        order = asc(Fact.plausibility)
    elif order_str == "td":
        order = desc(Fact.typicality)
    elif order_str == "ta":
        order = asc(Fact.typicality)
    elif order_str == "sd":
        order = desc(Fact.saliency)
    elif order_str == "sa":
        order = asc(Fact.saliency)
    else:
        order = desc(Fact.plausibility)
    facts = Fact.query.order_by(order).paginate(page, app.config["FACTS_PER_PAGE"], False)
    next_url = url_for('explorer.home', page=facts.next_num, order=order_str) if facts.has_next else None
    prev_url = url_for('explorer.home', page=facts.prev_num, order=order_str) if facts.has_prev else None
    return render_template("explorer.html", facts=facts.items, next_url=next_url, prev_url=prev_url, order=order_str)


@bp.route("/fill")
def fill():
    facts = read_facts(os.path.abspath(os.path.dirname(__file__)) + "/../tests/quasimodo_sample.tsv")
    add_all_facts_to_db(facts, db)
    return "Done"
