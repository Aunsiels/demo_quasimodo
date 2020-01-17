import json

from quasimodo_website import DB


class TabooCard(DB.Model):

    id = DB.Column(DB.Integer, primary_key=True)
    word_to_guess = DB.Column(DB.String(124))
    forbidden_words = DB.Column(DB.String(1024))

    def get_forbidden_words(self):
        return json.loads(self.forbidden_words)

    def set_forbidden_words(self, words):
        self.forbidden_words = json.dumps(words)
