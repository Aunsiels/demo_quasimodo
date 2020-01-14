import json

from quasimodo_website import db


class TabooCard(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    word_to_guess = db.Column(db.String(124))
    forbidden_words = db.Column(db.String(1024))

    def get_forbidden_words(self):
        return json.loads(self.forbidden_words)

    def set_forbidden_words(self, words):
        self.forbidden_words = json.dumps(words)