import os

from flask import render_template, session, request, jsonify

from quasimodo_website.codenames.blueprint import BP
from quasimodo_website.codenames.codenames import Codenames, CodenameColor
from quasimodo_website.codenames.codenames_agents import CodenamesMaster, Clue
from quasimodo_website.codenames.stop_the_game_players import \
    StopTheGameOperative, WaitForActionException, ClueGivenException, \
    QuasimodoSpyMasterWhenStopping

CODENAMES_FILE = FILENAME = os.path.dirname(os.path.realpath(__file__)) + \
                            "/../tests/codenames_words.txt"


@BP.route("/")
def home():
    codenames = Codenames.from_filename(CODENAMES_FILE)
    codenames_master = CodenamesMaster(
        codenames,
        red_spymaster=QuasimodoSpyMasterWhenStopping(
            codenames,
            CodenameColor.RED),
        red_operative=StopTheGameOperative(codenames,
                                           CodenameColor.RED,
                                           None,
                                           False)
    )
    return _play(codenames, codenames_master)


def _play(codenames, codenames_master):
    try:
        codenames_master.run_game()
    except WaitForActionException as _:
        session["codenames"] = codenames.to_json()
        return render_template("codenames.html",
                               codenames=codenames,
                               message="Choose another card")
    except ClueGivenException as e:
        session["codenames"] = codenames.to_json()
        clue = e.clue
        session["clue"] = str(clue.word) + "," + str(clue.occurrences)
        message = "Clue Given: " + str(clue.word) + ", " + str(
            clue.occurrences)
        return render_template("codenames.html",
                               codenames=codenames,
                               message=message)
    session["codenames"] = codenames.to_json()
    return render_template(
        "codenames_full.html",
        codenames=codenames,
        message="Game ended, winner is " + str(codenames.get_winner().name))


@BP.route("/guess_word")
def guess_word():
    guessed_word = request.args.get('word', None, type=str)
    codenames_json = session.get("codenames", None)
    if codenames_json is None:
        return jsonify({"error": "No game was started"})
    if guessed_word is None:
        return jsonify({"error": "No word was given"})
    codenames = Codenames.from_json(codenames_json)
    current_clue = session.get("clue", None)
    if codenames.has_played_already or current_clue is None:
        current_clue = None
    else:
        word, occ = current_clue.split(",")
        current_clue = Clue(word, occ)
    codenames_master = CodenamesMaster(
        codenames,
        red_spymaster=QuasimodoSpyMasterWhenStopping(
            codenames,
            CodenameColor.RED,
            word_given=current_clue),
        red_operative=StopTheGameOperative(codenames,
                                           CodenameColor.RED,
                                           guessed_word,
                                           False)
    )
    return _play(codenames, codenames_master)


@BP.route("/pass")
def pass_turn():
    codenames_json = session.get("codenames", None)
    if codenames_json is None:
        return jsonify({"error": "No game was started"})
    codenames = Codenames.from_json(codenames_json)
    codenames_master = CodenamesMaster(
        codenames,
        red_spymaster=QuasimodoSpyMasterWhenStopping(
            codenames,
            CodenameColor.RED),
        red_operative=StopTheGameOperative(codenames,
                                           CodenameColor.RED,
                                           None,
                                           True)
    )
    return _play(codenames, codenames_master)
