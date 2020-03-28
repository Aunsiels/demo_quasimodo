import os
import unittest

from quasimodo_website.codenames.codenames import N_CARDS, Codenames, \
    read_predefined_words, CodenameColor, GameNotFinishedException, \
    GameFinishedException, DidNotPlayException, NotYourTurnException
from quasimodo_website.codenames.codenames_agents import CodenamesMaster

FILENAME = os.path.dirname(os.path.realpath(__file__)) + "/codenames_words.txt"


class TestCodenames(unittest.TestCase):

    def setUp(self) -> None:
        self.codenames = Codenames.from_filename(FILENAME)
        self.red_cards = \
            self.codenames.get_all_words_by_color(CodenameColor.RED)
        self.blue_cards = \
            self.codenames.get_all_words_by_color(CodenameColor.BLUE)

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
        codenames2 = Codenames.from_filename(FILENAME)
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
            codenames = Codenames.from_filename(FILENAME)
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
            codenames = Codenames.from_filename(FILENAME)
            if codenames.get_current_player() is CodenameColor.RED:
                found_red = True
            else:
                found_blue = True
        self.assertTrue(found_red and found_blue)

    def test_always_same_starting_color_for_a_game(self):
        starting_colors = [self.codenames.get_current_player()
                           for _ in range(100)]
        self.assertEqual(1, len(set(starting_colors)))

    def test_starting_color_has_more_cards(self):
        for _ in range(100):
            codenames = Codenames.from_filename(FILENAME)
            starting_color = codenames.get_current_player()
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
            blue_cards_after = \
                self.codenames.get_remaining_words_by_color(CodenameColor.BLUE)
            blue_cards = \
                self.codenames.get_all_words_by_color(CodenameColor.BLUE)
            self.assertEqual(len(blue_cards_before), len(blue_cards_after) + 1)
            self.assertEqual(blue_cards, blue_cards_before)
        else:
            red_cards_before = self.red_cards
            self.codenames.guess(red_cards_before[0], CodenameColor.RED)
            red_cards_after = \
                self.codenames.get_remaining_words_by_color(CodenameColor.RED)
            red_cards = \
                self.codenames.get_all_words_by_color(CodenameColor.RED)
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
        self.assertIn(self.codenames.get_current_player(),
                      [CodenameColor.RED, CodenameColor.BLUE])

    def test_cannot_pass_without_playing(self):
        self.assertFalse(self.codenames.can_pass())
        with self.assertRaises(DidNotPlayException):
            self.codenames.pass_turn(self.codenames.get_current_player())

    def test_can_pass_if_played(self):
        current_player = self.codenames.get_current_player()
        self.guess_a_card_for_current_player()
        self.assertTrue(self.codenames.can_pass())
        self.codenames.pass_turn(self.codenames.get_current_player())
        self.assertNotEqual(current_player,
                            self.codenames.get_current_player())

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
        self.codenames.guess(self.codenames.assassin_card,
                             self.codenames.get_current_player())
        with self.assertRaises(GameFinishedException):
            self.codenames.pass_turn(self.codenames.get_current_player())

    def test_get_all_remaining_cards(self):
        self.assertEqual(len(self.codenames.get_remaining_word()),
                         N_CARDS)
        self.guess_a_card_for_current_player()
        self.assertEqual(len(self.codenames.get_remaining_word()),
                         N_CARDS - 1)

    def test_run_dummy_game(self):
        game_master = CodenamesMaster(self.codenames)
        self.assertIsNotNone(game_master.run_game())

    def test_good_clue(self):
        self.assertTrue(self.codenames.is_valid_clue("zxy"))

    def test_clue_in_words(self):
        word = self.codenames.get_words()[0]
        self.assertFalse(self.codenames.is_valid_clue(word))

    def test_sub_word(self):
        word = self.codenames.get_words()[0]
        self.assertFalse(self.codenames.is_valid_clue(word[:int(len(word)/2)]))

    def test_contain_word(self):
        word = self.codenames.get_words()[0]
        self.assertFalse(self.codenames.is_valid_clue(word + "s"))

    def test_invalid_capital_letter(self):
        word = self.codenames.get_words()[0]
        self.assertFalse(self.codenames.is_valid_clue(word.lower()))

    def test_to_json(self):
        self.guess_a_card_for_current_player()
        json_s = self.codenames.to_json()
        codenames_copy = Codenames.from_json(json_s)
        self.assertTrue(codenames_copy.can_pass())

    def test_to_json2(self):
        self.codenames.current_player = CodenameColor.RED
        for card in self.red_cards:
            self.codenames.guess(card, CodenameColor.RED)
        json_s = self.codenames.to_json()
        codenames_copy = Codenames.from_json(json_s)
        self.assertTrue(codenames_copy.is_finished())
        self.assertEqual(codenames_copy.get_winner(), CodenameColor.RED)


if __name__ == '__main__':
    unittest.main()
