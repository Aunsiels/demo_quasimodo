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
        self.current_player = random.choice([CodenameColor.RED, CodenameColor.BLUE])
        self.initialize_color_cards()
        self.found_assassin = False
        self.has_played_already = False

    def initialize_words(self, filename):
        predefined_words = read_predefined_words(filename)
        self.words = random.sample(predefined_words, k=N_CARDS)

    def initialize_color_cards(self):
        random_indexes = random.sample(range(N_CARDS), k=N_CARDS_TO_GUESS + 1)
        middle_index_under = int(N_CARDS_TO_GUESS / 2)
        splitting_index = middle_index_under if self.current_player is CodenameColor.BLUE else middle_index_under + 1
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
        return self.current_player

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
        if self.current_player != color:
            raise NotYourTurnException
        self.has_played_already = True
        if word in self.red_cards_remaining:
            self.red_cards_remaining.remove(word)
            if color == CodenameColor.BLUE:
                self.current_player = CodenameColor.RED
        if word in self.blue_cards_remaining:
            self.blue_cards_remaining.remove(word)
            if color == CodenameColor.RED:
                self.current_player = CodenameColor.BLUE
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

    def get_current_player(self):
        return self.current_player

    def pass_turn(self, color):
        if self.is_finished():
            raise GameFinishedException
        if not self.has_played_already:
            raise DidNotPlayException
        if color != self.current_player:
            raise NotYourTurnException
        if self.current_player == CodenameColor.RED:
            self.current_player = CodenameColor.BLUE
        else:
            self.current_player = CodenameColor.RED
        self.has_played_already = False


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


class DidNotPlayException(Exception):
    pass


class NotYourTurnException(Exception):
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

    def test_guess_good_one(self):
        if self.codenames.current_player == CodenameColor.BLUE:
            blue_cards_before = self.blue_cards
            self.codenames.guess(blue_cards_before[0], CodenameColor.BLUE)
            blue_cards_after = self.codenames.get_remaining_words_by_color(CodenameColor.BLUE)
            blue_cards = self.codenames.get_all_words_by_color(CodenameColor.BLUE)
            self.assertEqual(len(blue_cards_before), len(blue_cards_after) + 1)
            self.assertEqual(blue_cards, blue_cards_before)
        else:
            red_cards_before = self.red_cards
            self.codenames.guess(red_cards_before[0], CodenameColor.RED)
            red_cards_after = self.codenames.get_remaining_words_by_color(CodenameColor.RED)
            red_cards = self.codenames.get_all_words_by_color(CodenameColor.RED)
            self.assertEqual(len(red_cards_before), len(red_cards_after) + 1)
            self.assertEqual(red_cards, red_cards_before)

    def test_guess_assassin(self):
        self.codenames.current_player = CodenameColor.RED
        assassin_card = self.codenames.get_assassin_card()
        self.codenames.guess(assassin_card, CodenameColor.RED)
        self.assertTrue(self.codenames.is_finished())

    def test_get_winner_assassin(self):
        assassin_card = self.codenames.get_assassin_card()
        if self.codenames.get_current_player() == CodenameColor.RED:
            self.codenames.guess(assassin_card, CodenameColor.RED)
            self.assertEqual(self.codenames.get_winner(), CodenameColor.BLUE)
        else:
            self.codenames.guess(assassin_card, CodenameColor.BLUE)
            self.assertEqual(self.codenames.get_winner(), CodenameColor.RED)

    def test_winner_all_cards_red(self):
        self.codenames.current_player = CodenameColor.RED
        for card in self.red_cards:
            self.codenames.guess(card, CodenameColor.RED)
        self.assertTrue(self.codenames.is_finished())
        self.assertEqual(self.codenames.get_winner(), CodenameColor.RED)

    def test_winner_all_cards_blue(self):
        self.codenames.current_player = CodenameColor.RED
        for card in self.blue_cards:
            self.codenames.guess(card, CodenameColor.RED)
            self.codenames.current_player = CodenameColor.RED
        self.assertTrue(self.codenames.is_finished())
        self.assertEqual(self.codenames.get_winner(), CodenameColor.BLUE)

    def test_cannot_guess_once_game_is_finished(self):
        if self.codenames.get_current_player() == CodenameColor.RED:
            for card in self.red_cards:
                self.codenames.guess(card, CodenameColor.RED)
            with self.assertRaises(GameFinishedException) as _:
                self.codenames.guess(self.blue_cards[0], CodenameColor.RED)
        else:
            for card in self.blue_cards:
                self.codenames.guess(card, CodenameColor.BLUE)
            with self.assertRaises(GameFinishedException) as _:
                self.codenames.guess(self.red_cards[0], CodenameColor.BLUE)

    def test_get_current_player(self):
        self.assertIn(self.codenames.get_current_player(), [CodenameColor.RED, CodenameColor.BLUE])

    def test_cannot_pass_without_playing(self):
        with self.assertRaises(DidNotPlayException):
            self.codenames.pass_turn(self.codenames.get_current_player())

    def test_can_pass_if_played(self):
        current_player = self.codenames.get_current_player()
        self.guess_a_card_for_current_player()
        self.codenames.pass_turn(self.codenames.get_current_player())
        self.assertNotEqual(current_player, self.codenames.get_current_player())

    def guess_a_card_for_current_player(self):
        if self.codenames.get_current_player() == CodenameColor.RED:
            self.codenames.guess(self.red_cards[0], CodenameColor.RED)
        else:
            self.codenames.guess(self.blue_cards[0], CodenameColor.BLUE)

    def test_cannot_pass_if_it_is_not_our_turn(self):
        self.guess_a_card_for_current_player()
        current_player = self.codenames.get_current_player()
        if current_player == CodenameColor.RED:
            other_player = CodenameColor.BLUE
        else:
            other_player = CodenameColor.RED
        with self.assertRaises(NotYourTurnException):
            self.codenames.pass_turn(other_player)

    def test_cannot_pass_twice_without_guessing_again(self):
        self.guess_a_card_for_current_player()
        self.codenames.pass_turn(self.codenames.get_current_player())
        with self.assertRaises(DidNotPlayException):
            self.codenames.pass_turn(self.codenames.get_current_player())

    def test_cannot_guess_if_it_is_not_your_turn(self):
        if self.codenames.get_current_player() == CodenameColor.RED:
            with self.assertRaises(NotYourTurnException):
                self.codenames.guess(self.blue_cards[0], CodenameColor.BLUE)
        else:
            with self.assertRaises(NotYourTurnException):
                self.codenames.guess(self.red_cards[0], CodenameColor.RED)

    def test_cannot_keep_guessing_if_wrong_card(self):
        self.codenames.current_player = CodenameColor.RED
        self.codenames.guess(self.blue_cards[0], CodenameColor.RED)
        with self.assertRaises(NotYourTurnException):
            self.codenames.guess(self.blue_cards[1], CodenameColor.RED)

    def test_starting_current_player_has_one_more_card(self):
        if self.codenames.get_current_player() == CodenameColor.RED:
            self.assertEqual(len(self.red_cards), len(self.blue_cards) + 1)
        else:
            self.assertEqual(len(self.blue_cards), len(self.red_cards) + 1)

    def test_cannot_pass_if_finished(self):
        self.codenames.guess(self.codenames.assassin_card, self.codenames.get_current_player())
        with self.assertRaises(GameFinishedException):
            self.codenames.pass_turn(self.codenames.get_current_player())


if __name__ == '__main__':
    unittest.main()
