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
        self.red_cards_remaining = None
        self.blue_cards_remaining = None
        self.winner = None
        self.initialize_words(filename)
        self.starting_color = random.choice([CodenameColor.RED, CodenameColor.BLUE])
        self.initialize_color_cards()
        self.found_assassin = False

    def initialize_words(self, filename):
        predefined_words = read_predefined_words(filename)
        self.words = random.sample(predefined_words, k=N_CARDS)

    def initialize_color_cards(self):
        random_indexes = random.sample(range(N_CARDS), k=N_CARDS_TO_GUESS + 1)
        middle_index_under = int(N_CARDS_TO_GUESS / 2)
        splitting_index = middle_index_under if self.starting_color is CodenameColor.BLUE else middle_index_under + 1
        self.red_cards = [self.words[x] for x in random_indexes[:splitting_index]]
        self.red_cards_remaining = self.red_cards[:]
        self.blue_cards = [self.words[x] for x in random_indexes[splitting_index:N_CARDS_TO_GUESS]]
        self.blue_cards_remaining = self.blue_cards[:]
        self.assassin_card = self.words[random_indexes[-1]]

    def get_words(self):
        return self.words

    def get_all_words_by_color(self, color):
        if color is CodenameColor.RED:
            return self.red_cards
        else:
            return self.blue_cards

    def get_starting_color(self):
        return self.starting_color

    def get_assassin_card(self):
        return self.assassin_card

    def is_finished(self):
        return self.found_assassin or \
               len(self.red_cards_remaining) == 0 or \
               len(self.blue_cards_remaining) == 0

    def get_winner(self):
        if self.is_finished():
            if self.winner is not None:
                return self.winner
            if len(self.red_cards_remaining) == 0:
                return CodenameColor.RED
            if len(self.blue_cards_remaining) == 0:
                return CodenameColor.BLUE
        raise GameNotFinishedException

    def guess(self, word, color):
        if self.is_finished():
            raise GameFinishedException
        if word in self.red_cards_remaining:
            self.red_cards_remaining.remove(word)
        if word in self.blue_cards_remaining:
            self.blue_cards_remaining.remove(word)
        if word == self.assassin_card:
            self.found_assassin = True
            if color == CodenameColor.RED:
                self.winner = CodenameColor.BLUE
            else:
                self.winner = CodenameColor.RED

    def get_remaining_words_by_color(self, color):
        if color is CodenameColor.RED:
            return self.red_cards_remaining
        else:
            return self.blue_cards_remaining


def read_predefined_words(filename):
    predefined_words = []
    with open(filename) as predefined_words_file:
        for line in predefined_words_file:
            predefined_words.append(line.strip())
    return predefined_words


class CodenameColor(Enum):
    RED = auto()
    BLUE = auto()


class GameNotFinishedException(Exception):
    pass


class GameFinishedException(Exception):
    pass


class TestCodenames(unittest.TestCase):

    def setUp(self) -> None:
        self.codenames = Codenames(FILENAME)
        self.red_cards = self.codenames.get_all_words_by_color(CodenameColor.RED)
        self.blue_cards = self.codenames.get_all_words_by_color(CodenameColor.BLUE)

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
        self.assertTrue(len(self.red_cards) >= 8)

    def test_get_blue_cards(self):
        self.assertTrue(len(self.blue_cards) >= 8)

    def test_number_cards_to_guess(self):
        self.assertEqual(len(self.red_cards) + len(self.blue_cards), 17)

    def test_color_words_are_in_words(self):
        words = self.codenames.get_words()
        self.assertTrue(all([x in words for x in self.red_cards]))
        self.assertTrue(all([x in words for x in self.blue_cards]))

    def test_color_words_are_different(self):
        colored_cards = set(self.red_cards).union(set(self.blue_cards))
        self.assertEqual(len(colored_cards), 17)

    def test_all_indexes_are_visited(self):
        index_explored_red = [False for _ in range(N_CARDS)]
        index_explored_blue = [False for _ in range(N_CARDS)]
        for _ in range(100):
            codenames = Codenames(FILENAME)
            words = codenames.get_words()
            red_cards = codenames.get_all_words_by_color(CodenameColor.RED)
            for card in red_cards:
                index_explored_red[words.index(card)] = True
            blue_cards = codenames.get_all_words_by_color(CodenameColor.BLUE)
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
            cards = codenames.get_all_words_by_color(starting_color)
            self.assertEqual(len(cards), 9)

    def test_get_assassin_car(self):
        assassin_card = self.codenames.get_assassin_card()
        self.assertTrue(isinstance(assassin_card, str))

    def test_assassin_card_in_words(self):
        words = self.codenames.words
        assassin_card = self.codenames.get_assassin_card()
        self.assertIn(assassin_card, words)

    def test_assert_not_in_red_or_blue(self):
        blue_cards = set(self.blue_cards)
        assassin_card = self.codenames.get_assassin_card()
        self.assertNotIn(assassin_card, self.red_cards)
        self.assertNotIn(assassin_card, blue_cards)

    def test_is_game_finished(self):
        self.assertFalse(self.codenames.is_finished())

    def test_get_winner_exception(self):
        with self.assertRaises(GameNotFinishedException) as _:
            self.codenames.get_winner()

    def test_guess_good_one_red(self):
        red_cards_before = self.red_cards
        self.codenames.guess(red_cards_before[0], CodenameColor.RED)
        red_cards_after = self.codenames.get_remaining_words_by_color(CodenameColor.RED)
        red_cards = self.codenames.get_all_words_by_color(CodenameColor.RED)
        self.assertEqual(len(red_cards_before), len(red_cards_after) + 1)
        self.assertEqual(red_cards, red_cards_before)

    def test_guess_good_one_blue(self):
        blue_cards_before = self.blue_cards
        self.codenames.guess(blue_cards_before[0], CodenameColor.RED)
        blue_cards_after = self.codenames.get_remaining_words_by_color(CodenameColor.BLUE)
        blue_cards = self.codenames.get_all_words_by_color(CodenameColor.BLUE)
        self.assertEqual(len(blue_cards_before), len(blue_cards_after) + 1)
        self.assertEqual(blue_cards, blue_cards_before)

    def test_guess_assassin(self):
        assassin_card = self.codenames.get_assassin_card()
        self.codenames.guess(assassin_card, CodenameColor.RED)
        self.assertTrue(self.codenames.is_finished())

    def test_get_winner_assassin(self):
        assassin_card = self.codenames.get_assassin_card()
        self.codenames.guess(assassin_card, CodenameColor.RED)
        self.assertEqual(self.codenames.get_winner(), CodenameColor.BLUE)

    def test_winner_all_cards_red(self):
        for card in self.red_cards:
            self.codenames.guess(card, CodenameColor.RED)
        self.assertTrue(self.codenames.is_finished())
        self.assertEqual(self.codenames.get_winner(), CodenameColor.RED)

    def test_winner_all_cards_blue(self):
        for card in self.blue_cards:
            self.codenames.guess(card, CodenameColor.RED)
        self.assertTrue(self.codenames.is_finished())
        self.assertEqual(self.codenames.get_winner(), CodenameColor.BLUE)

    def test_cannot_guess_once_game_is_finished(self):
        for card in self.red_cards:
            self.codenames.guess(card, CodenameColor.RED)
        with self.assertRaises(GameFinishedException) as _:
            self.codenames.guess(self.blue_cards[0], CodenameColor.RED)


if __name__ == '__main__':
    unittest.main()
