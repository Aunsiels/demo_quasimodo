import os

from flask import render_template, request, url_for
from flask import current_app as app
from sqlalchemy import desc, asc
from werkzeug.utils import redirect

from demo import db
from demo.explorer import bp
from demo.models.fact import Fact, read_facts, add_all_facts_to_db
from demo.models.search_form import SearchForm


@bp.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    order_str = request.args.get("order", "pd", type=str)
    order = get_order(order_str)
    subject = request.args.get("subject", None, type=str)
    predicate = request.args.get("predicate", None, type=str)
    obj = request.args.get("object", None, type=str)
    modality = request.args.get("modality", None, type=str)
    polarity = request.args.get("polarity", None, type=str)
    if polarity is not None:
        polarity = polarity == "1"

    facts = Fact.query
    if subject:
        facts = facts.filter_by(subject=subject)
    if predicate:
        facts = facts.filter_by(predicate=predicate)
    if obj:
        facts = facts.filter_by(object=obj)
    if modality:
        search = "%{}%".format(modality)
        facts = facts.filter(Fact.modality.like(search))
    if polarity is not None:
        print(polarity)
        facts = facts.filter_by(is_negative=polarity)

    facts = facts.order_by(order).paginate(page, app.config["FACTS_PER_PAGE"], False)
    new_args = request.args.copy()
    new_args["page"] = facts.next_num
    next_url = url_for('explorer.home', **new_args) if facts.has_next else None
    new_args["page"] = facts.prev_num
    prev_url = url_for('explorer.home', **new_args) if facts.has_prev else None
    if "page" in new_args:
        del new_args["page"]
    if "order" in new_args:
        del new_args["order"]
    return render_template("explorer.html", facts=facts.items,
                           next_url=next_url,
                           prev_url=prev_url,
                           order=order_str,
                           additional_args=new_args)


def get_order(order_str):
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
    return order


@bp.route("/fill")
def fill():
    facts = read_facts(os.path.abspath(os.path.dirname(__file__)) + "/../tests/quasimodo_sample.tsv")
    add_all_facts_to_db(facts, db)
    return "Done"


@bp.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        args = {}
        if form.subject.data.strip():
            args["subject"] = form.subject.data.strip().lower()
        if form.predicate.data.strip():
            args["predicate"] = form.predicate.data.strip().lower()
        if form.object.data.strip():
            args["object"] = form.object.data.strip().lower()
        if form.modality.data.strip():
            args["modality"] = form.modality.data.strip().lower()
        if form.polarity.data == "Positive":
            args["polarity"] = 0
        elif form.polarity.data == "Negative":
            args["polarity"] = 1

        args["page"] = request.args.get('page', 1, type=int)
        args["order"] = request.args.get("order", "pd", type=str)
        return redirect(url_for("explorer.home", **args))
    return render_template("search.html", form=form)
