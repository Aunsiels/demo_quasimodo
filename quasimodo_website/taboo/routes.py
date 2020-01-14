import os
import random

from flask import session, request, jsonify

from quasimodo_website.models.taboo_card import TabooCard
from quasimodo_website.taboo import bp
from quasimodo_website import db


@bp.route("/")
def home():
    session['words_given'] = []
    max_row = TabooCard.query.count()
    if max_row == 0:
        return ""
    rand_number = random.randrange(0, max_row)
    random_card = TabooCard.query[rand_number]
    session["word_to_guess"] = random_card.word_to_guess
    session["forbidden_words"] = random_card.get_forbidden_words()
    return ""


@bp.route("/give_word")
def give_word():
    given_word = request.args.get('word', None, type=str)
    if given_word is not None:
        session["words_given"] = session.get("words_given", [])
        session["words_given"].append(given_word)
    return jsonify({})


@bp.route("/get_given_words")
def get_given_words():
    return jsonify(session.get("words_given", []))


@bp.route("/get_word_to_guess")
def get_word_to_guess():
    return jsonify({"word_to_guess": session.get("word_to_guess", "")})


@bp.route("/initialize")
def initialize():
    n_facts = TabooCard.query.count()
    if n_facts == 0:
        cards = []
        with open(os.path.abspath(os.path.dirname(__file__)) + "/../../data/taboo.tsv") as f:
            for line in f:
                line = line.strip().split("\t")
                taboo_card = TabooCard(word_to_guess=line[0])
                taboo_card.set_forbidden_words(line[1:])
                cards.append(taboo_card)
        db.session.add_all(cards)
        db.session.commit()
    return jsonify({"status": "Done"})