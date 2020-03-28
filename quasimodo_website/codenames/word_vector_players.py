from itertools import combinations

import gensim.downloader as api
import numpy as np

from quasimodo_website.codenames.codenames import CodenameColor
from quasimodo_website.codenames.codenames_agents import Operative, SpyMaster, \
    Clue

word_vectors = api.load(
    "glove-wiki-gigaword-50")  # "word2vec-google-news-300")


# From "Cooperation and Codenames:
# Understanding Natural Language Processing via Codenames"


class WordVectorOperative(Operative):

    def __init__(self, codenames, color):
        super().__init__(codenames, color)
        self.n_remaining = 0
        self.last_given_word = None

    def make_contact(self):
        remaining_words = self.codenames.get_remaining_word()
        best_word = None
        best_similarity = -2
        for word in remaining_words:
            similarity = word_vectors.similarity(
                word.lower(),
                self.last_given_word)
            if similarity > best_similarity:
                best_word = word
                best_similarity = similarity
        self.n_remaining -= 1
        print("Guessed:", best_word)
        return best_word

    def receive_clue(self, clue):
        self.last_given_word = clue.word.lower()
        self.n_remaining = clue.occurrences

    def want_pass(self):
        return self.n_remaining == 0


THRESHOLD = 0.5
MAX_GROUP = 3


class WordVectorSpyMaster(SpyMaster):

    def give_clue(self):
        good_words = self.codenames.get_remaining_words_by_color(
            self.color
        )
        print("Remaining:", good_words)
        if self.color == CodenameColor.RED:
            other_color = CodenameColor.BLUE
        else:
            other_color = CodenameColor.RED
        bad_words = self.codenames.get_remaining_words_by_color(
            other_color
        ) + [self.codenames.get_assassin_card()]
        good_words = [x.lower() for x in good_words]
        bad_words = [x.lower() for x in bad_words]
        i_to_word = list(word_vectors.vocab)

        similarities = [dict() for _ in range(len(word_vectors.vocab))]
        for word in good_words + bad_words:
            for i, similarity in enumerate(
                    word_vectors.most_similar(positive=[word], topn=None)):
                similarities[i][word] = similarity

        best_i = 0
        best_word = None
        best_similarity = -2
        for i in range(1, min(MAX_GROUP, len(good_words) + 1)):
            for r_c in combinations(good_words, i):
                similarities_temp = [
                    word_vectors.most_similar(positive=[word], topn=None)
                    for word in r_c
                ]
                similarities_temp = np.array(similarities_temp)
                if i > 1:
                    similarities_temp = np.min(np.array(similarities_temp),
                                               axis=0)
                similarities_temp = similarities_temp.reshape((-1,))
                ordered_words = [
                    x[0]
                    for x in sorted(
                        enumerate(similarities_temp),
                        key=lambda x: x[1],
                        reverse=True
                    )
                ]
                for word_idx in ordered_words:
                    best_bad = -2
                    for b_w in bad_words:
                        similarity_bad = similarities[word_idx][b_w]
                        if similarity_bad > best_bad:
                            best_bad = similarity_bad
                    worst_good = 2
                    for r_w in r_c:
                        similarity_good = similarities[word_idx][r_w]
                        worst_good = min(worst_good, similarity_good)
                    if ((worst_good > best_similarity or i > best_i) and
                            worst_good > best_bad and
                            worst_good > THRESHOLD):
                        word = i_to_word[word_idx]
                        if not self.codenames.is_valid_clue(word):
                            continue
                        best_similarity = worst_good
                        best_word = i_to_word[word_idx]
                        best_i = i
                        break
                    if worst_good < best_similarity:
                        break
        print("Clue:", best_word, best_i, best_similarity)
        return Clue(best_word, best_i)
