import os
import unittest
import random
from enum import Enum, auto

N_CARDS_TO_GUESS = 17

N_CARDS = 25

FILENAME = os.path.dirname(os.path.realpath(__file__)) + "/codenames_words.txt"


class Codenames(object):

    def __init__(self, filename):
        self.words = None
        self.red_cards = None
        self.blue_cards = None
        self.assassin_card = None
        self.initialize_words(filename)
        self.starting_color = random.choice([CodenameColor.RED, CodenameColor.BLUE])
        self.initialize_color_cards()

    def initialize_words(self, filename):
        predefined_words = read_predefined_words(filename)
        self.words = random.sample(predefined_words, k=N_CARDS)

    def initialize_color_cards(self):
        random_indexes = random.sample(range(N_CARDS), k=N_CARDS_TO_GUESS + 1)
        middle_index_under = int(N_CARDS_TO_GUESS / 2)
        splitting_index = middle_index_under if self.starting_color is CodenameColor.BLUE else middle_index_under + 1
        self.red_cards = [self.words[x] for x in random_indexes[:splitting_index]]
        self.blue_cards = [self.words[x] for x in random_indexes[splitting_index:N_CARDS_TO_GUESS]]
        self.assassin_card = self.words[random_indexes[-1]]

    def get_words(self):
        return self.words

    def get_words_by_color(self, color):
        if color is CodenameColor.RED:
            return self.red_cards
        else:
            return self.blue_cards

    def get_starting_color(self):
        return self.starting_color

    def get_assassin_card(self):
        return self.assassin_card
    c

def read_predefined_words(filename):
    predefined_words = []
    with open(filename) as predefined_words_file:
        for line in predefined_words_file:
            predefined_words.append(line.strip())
    return predefined_words


class CodenameColor(Enum):
    RED = auto()
    BLUE = auto()


class TestCodenames(unittest.TestCase):

    def setUp(self) -> None:
        self.codenames = Codenames(FILENAME)

    def test_get_all_words_number(self):
        words = self.codenames.get_words()
        self.assertEqual(len(words), N_CARDS)

    def test_get_all_words_different(self):
        words = set(self.codenames.get_words())
        self.assertEqual(len(words), N_CARDS)

    def test_get_all_words_string(self):
        words = self.codenames.get_words()
        self.assertTrue(all([isinstance(x, str) for x in words]))

    def test_all_words_in_predefined_list(self):
        words = self.codenames.get_words()
        predefined_words = read_predefined_words(FILENAME)
        self.assertTrue(all([x in predefined_words for x in words]))

    def test_all_words_are_different_from_one_game_to_another(self):
        words = self.codenames.get_words()
        codenames2 = Codenames(FILENAME)
        words2 = codenames2.get_words()
        self.assertNotEqual(words, words2)

    def test_words_remain_the_same(self):
        words = self.codenames.get_words()
        words2 = self.codenames.get_words()
        self.assertEqual(words, words2)

    def test_get_red_cards(self):
        red_cards = self.codenames.get_words_by_color(CodenameColor.RED)
        self.assertTrue(len(red_cards) >= 8)

    def test_get_blue_cards(self):
        blue_cards = self.codenames.get_words_by_color(CodenameColor.BLUE)
        self.assertTrue(len(blue_cards) >= 8)

    def test_number_cards_to_guess(self):
        red_cards = self.codenames.get_words_by_color(CodenameColor.RED)
        blue_cards = self.codenames.get_words_by_color(CodenameColor.BLUE)
        self.assertEqual(len(red_cards) + len(blue_cards), 17)

    def test_color_words_are_in_words(self):
        red_cards = self.codenames.get_words_by_color(CodenameColor.RED)
        blue_cards = self.codenames.get_words_by_color(CodenameColor.BLUE)
        words = self.codenames.get_words()
        self.assertTrue(all([x in words for x in red_cards]))
        self.assertTrue(all([x in words for x in blue_cards]))

    def test_color_words_are_different(self):
        red_cards = set(self.codenames.get_words_by_color(CodenameColor.RED))
        blue_cards = set(self.codenames.get_words_by_color(CodenameColor.BLUE))
        colored_cards = red_cards.union(blue_cards)
        self.assertEqual(len(colored_cards), 17)

    def test_all_indexes_are_visited(self):
        index_explored_red = [False for _ in range(N_CARDS)]
        index_explored_blue = [False for _ in range(N_CARDS)]
        for _ in range(100):
            codenames = Codenames(FILENAME)
            words = codenames.get_words()
            red_cards = codenames.get_words_by_color(CodenameColor.RED)
            for card in red_cards:
                index_explored_red[words.index(card)] = True
            blue_cards = codenames.get_words_by_color(CodenameColor.BLUE)
            for card in blue_cards:
                index_explored_blue[words.index(card)] = True
        self.assertTrue(all(index_explored_red))
        self.assertTrue(all(index_explored_blue))

    def test_not_always_same_starting_color_for_different_games(self):
        found_red = False
        found_blue = False
        for _ in range(100):
            codenames = Codenames(FILENAME)
            if codenames.get_starting_color() is CodenameColor.RED:
                found_red = True
            else:
                found_blue = True
        self.assertTrue(found_red and found_blue)

    def test_always_same_starting_color_for_a_game(self):
        starting_colors = [self.codenames.get_starting_color()
                           for _ in range(100)]
        self.assertEqual(1, len(set(starting_colors)))

    def test_starting_color_has_more_cards(self):
        for _ in range(100):
            codenames = Codenames(FILENAME)
            starting_color = codenames.get_starting_color()
            cards = codenames.get_words_by_color(starting_color)
            self.assertEqual(len(cards), 9)

    def test_get_assassin_car(self):
        assassin_card = self.codenames.get_assassin_card()
        self.assertTrue(isinstance(assassin_card, str))

    def test_assassin_card_in_words(self):
        words = self.codenames.words
        assassin_card = self.codenames.get_assassin_card()
        self.assertIn(assassin_card, words)

    def test_assert_not_in_red_or_blue(self):
        red_cards = set(self.codenames.get_words_by_color(CodenameColor.RED))
        blue_cards = set(self.codenames.get_words_by_color(CodenameColor.BLUE))
        assassin_card = self.codenames.get_assassin_card()
        self.assertNotIn(assassin_card, red_cards)
        self.assertNotIn(assassin_card, blue_cards)


if __name__ == '__main__':
    unittest.main()
