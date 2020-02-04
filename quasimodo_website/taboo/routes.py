import os
import random

from flask import session, request, jsonify, render_template, current_app
from sqlalchemy import func

from quasimodo_website.models import Fact
from quasimodo_website.models.taboo_card import TabooCard
from quasimodo_website.taboo.blueprint import BP
from quasimodo_website import DB


@BP.route("/")
def home():
    return render_template("taboo.html")


@BP.route("/start_new_game")
def start_new_game():
    session['words_given'] = []
    max_row = TabooCard.query.count()
    if max_row == 0:
        return jsonify({"error": "No cards"})
    rand_number = random.randrange(0, max_row)
    random_card = TabooCard.query[rand_number]
    session["word_to_guess"] = random_card.word_to_guess
    session["forbidden_words"] = random_card.get_forbidden_words()
    session["wrongly_guessed"] = []
    return jsonify({"word_to_guess": random_card.word_to_guess,
                    "forbidden_words": random_card.get_forbidden_words()})


def try_to_guess(words_given, wrongly_guessed,
                 score_criterion=Fact.plausibility):
    query = None
    if not words_given:
        return "No idea"
    for word in words_given:
        sub_query = Fact.query.filter(Fact.object.like("%" + word + "%"))\
                              .with_entities(Fact.subject, score_criterion)
        if query is None:
            query = sub_query
        else:
            query = query.union(sub_query)
    query = query.filter(Fact.subject.notin_(wrongly_guessed))\
                 .group_by(Fact.subject)
    query = query.with_entities(Fact.subject, func.max(score_criterion))
    results = query.all()
    if not results:
        return "No idea"
    best = max(results, key=lambda x: x[1])
    return best[0]


def preprocess_given_word(given_word):
    return given_word.lower()


def are_too_similar(first_word, second_word):
    return first_word in second_word or second_word in first_word


@BP.route("/give_word")
def give_word():
    given_word = request.args.get('word', None, type=str)
    if given_word is not None:
        given_word = preprocess_given_word(given_word)
        words_given = session.get("words_given", [])
        word_to_guess = session.get("word_to_guess", "")
        current_app.logger.info("Taboo: word to guess: " +
                                word_to_guess +
                                " word given: " + given_word)
        if are_too_similar(word_to_guess, given_word):
            return jsonify({"error": "The given word is too similar "
                                     "to the word to guess"})
        for forbidden_word in session.get("forbidden_words", []):
            if are_too_similar(given_word, forbidden_word):
                return jsonify({"error": "The given word is too similar "
                                         "to the forbidden word: "
                                         + str(forbidden_word)})
        if given_word in words_given:
            return jsonify({"error": "Word already given"})
        session["words_given"] = words_given
        session["words_given"].append(given_word)
    return jsonify({})


@BP.route("/guess_word")
def guess_word():
    guessed = try_to_guess(session.get("words_given", []),
                           session.get("wrongly_guessed", []))
    is_correct = guessed == session.get("word_to_guess", "")
    if not is_correct:
        session["wrongly_guessed"] = session.get("wrongly_guessed", [])
        session["wrongly_guessed"].append(guessed)
    current_app.logger.info("Guessed: " + guessed +
                            " for: " +
                            ", ".join(session.get("words_given", [])))
    return jsonify({"guessed": guessed,
                    "is_correct": is_correct})


@BP.route("/get_wrongly_guessed")
def get_wrongly_guessed():
    return jsonify(session.get("wrongly_guessed", []))


@BP.route("/get_given_words")
def get_given_words():
    return jsonify(session.get("words_given", []))


@BP.route("/get_word_to_guess")
def get_word_to_guess():
    return jsonify({"word_to_guess": session.get("word_to_guess", "")})


@BP.route("/get_forbidden_words")
def get_forbidden_words():
    return jsonify({"forbidden_words": session.get("forbidden_words", [])})


@BP.route("/initialize")
def initialize():
    n_facts = TabooCard.query.count()
    if n_facts == 0:
        cards = []
        with open(os.path.abspath(os.path.dirname(__file__)) +
                  "/../static/data/taboo.tsv") as taboo_card_file:
            for line in taboo_card_file:
                line = line.strip().split("\t")
                taboo_card = TabooCard(word_to_guess=line[0])
                taboo_card.set_forbidden_words(line[1:])
                cards.append(taboo_card)
        DB.session.add_all(cards)
        DB.session.commit()
    return jsonify({"status": "Done"})
