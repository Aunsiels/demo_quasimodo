import collections
import os
import unittest
import random
from enum import Enum, auto

N_CARDS_TO_GUESS = 17

N_CARDS = 25

FILENAME = os.path.dirname(os.path.realpath(__file__)) + "/codenames_words.txt"


class Codenames:

    def __init__(self, filename):
        self.words = None
        self.red_cards = None
        self.blue_cards = None
        self.assassin_card = None
        self.red_cards_remaining = None
        self.blue_cards_remaining = None
        self.winner = None
        self._initialize_words(filename)
        self.current_player = random.choice([CodenameColor.RED,
                                             CodenameColor.BLUE])
        self._initialize_color_cards()
        self.found_assassin = False
        self.has_played_already = False
        self.guessed_words = []

    def _initialize_words(self, filename):
        predefined_words = read_predefined_words(filename)
        self.words = random.sample(predefined_words, k=N_CARDS)

    def _initialize_color_cards(self):
        random_indexes = random.sample(range(N_CARDS), k=N_CARDS_TO_GUESS + 1)
        middle_index_under = int(N_CARDS_TO_GUESS / 2)
        splitting_index = \
            middle_index_under if self.current_player is CodenameColor.BLUE \
            else middle_index_under + 1
        self.red_cards = [self.words[x]
                          for x in random_indexes[:splitting_index]]
        self.red_cards_remaining = self.red_cards[:]
        self.blue_cards = [
            self.words[x]
            for x in random_indexes[splitting_index:N_CARDS_TO_GUESS]]
        self.blue_cards_remaining = self.blue_cards[:]
        self.assassin_card = self.words[random_indexes[-1]]

    def get_words(self):
        """
        Give the list of all words
        :return: the list of all words
        """
        return self.words

    def get_all_words_by_color(self, color):
        """
        Give the list of words by color
        :param color: the color, CodenameColor.RED or CodenameColor.BLUE
        :return: the list of words for the given color
        """
        if color is CodenameColor.RED:
            return self.red_cards
        else:
            return self.blue_cards

    def get_assassin_card(self):
        """
        Get the card of the assassin
        :return: the card of the assassin
        """
        return self.assassin_card

    def is_finished(self):
        """
        Check if the game is over
        :return: Whether the game is over or not
        """
        return self.found_assassin or \
            len(self.red_cards_remaining) == 0 or \
            len(self.blue_cards_remaining) == 0

    def get_winner(self):
        """
        If the game is finished, give the winner
        :return: The winner
        :raises: GameNotFinishedException
        """
        if self.is_finished():
            if self.winner is not None:
                return self.winner
            if len(self.red_cards_remaining) == 0:
                return CodenameColor.RED
            if len(self.blue_cards_remaining) == 0:
                return CodenameColor.BLUE
        raise GameNotFinishedException

    def guess(self, word, color):
        """
        Register someone guess
        :param word: The guessed word
        :param color: The team color
        :return: None
        :raises: GameFinishedException when the game is already over,
        NotYourTurnException if the wrong team played
        TODO: Only one extra guess
        """
        if self.is_finished():
            raise GameFinishedException
        if self.current_player != color:
            raise NotYourTurnException
        self.has_played_already = True
        self.guessed_words.append(word)
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

    def get_remaining_word(self):
        return set(self.words).difference(set(self.guessed_words))

    def get_remaining_words_by_color(self, color):
        """
        Get the remaining word for a color
        :param color: The color of the team
        :return: the list of remaining words to guess
        """
        if color is CodenameColor.RED:
            return self.red_cards_remaining
        else:
            return self.blue_cards_remaining

    def get_current_player(self):
        """
        Get the current team color
        :return: The current team color
        """
        return self.current_player

    def pass_turn(self, color):
        """
        Pass the turn
        :param color: The colour of the team
        :return: None
        :raises: GameFinishedException if the game is over,
        DidNotPlayException if the current team has not done at least one
        guess, NotYourTurnException if the non current team is trying to pass
        """
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

    def can_pass(self):
        """
        Checks if the current team can pass
        :return: Whether the current team can pass or not.
        """
        return not self.is_finished() and self.has_played_already


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


Clue = collections.namedtuple('Clue', 'word occurrences')


class SpyMaster:

    def __init__(self, codenames, color):
        self.codenames = codenames
        self.color = color

    def give_clue(self):
        """
        Give a clue
        :return: a clue
        """
        raise NotImplementedError


class Operative:

    def __init__(self, codenames, color):
        self.codenames = codenames
        self.color = color

    def make_contact(self):
        """
        Make a guess
        :return: a word to guess
        """
        raise NotImplementedError

    def receive_clue(self, clue):
        """
        Receive a clue from the spy master
        :param clue: The clue
        :return: None
        """
        raise NotImplementedError

    def want_pass(self):
        """
        Asks the operative if they want to pass
        :return: a bool
        """
        raise NotImplementedError


class SpyMaster2Players(SpyMaster):

    def give_clue(self):
        return Clue("BOT", 1)


class Operative2Players(Operative):

    def make_contact(self):
        return self.codenames.get_remaining_words_by_color(self.color)[0]

    def receive_clue(self, clue):
        pass

    def want_pass(self):
        return True


class CodenamesMaster:
    """
    Organize and run a game
    """

    def __init__(self,
                 codenames,
                 blue_spymaster=None,
                 red_spymaster=None,
                 blue_operative=None,
                 red_operative=None):
        self._codenames = codenames
        self._blue_spymaster = \
            blue_spymaster or SpyMaster2Players(codenames, CodenameColor.BLUE)
        self._red_spymaster = \
            red_spymaster or SpyMaster2Players(codenames, CodenameColor.RED)
        self._blue_operative = \
            blue_operative or Operative2Players(codenames, CodenameColor.BLUE)
        self._red_operative = \
            red_operative or Operative2Players(codenames, CodenameColor.RED)

    def _get_current_spymaster(self, color):
        if color == CodenameColor.BLUE:
            return self._blue_spymaster
        else:
            return self._red_spymaster

    def _get_current_operative(self, color):
        if color == CodenameColor.BLUE:
            return self._red_operative
        else:
            return self._blue_operative

    def run_game(self):
        """
        Run the game and return the winner
        :return: The winning team color
        """
        while not self._codenames.is_finished():
            current_color = self._codenames.get_current_player()
            current_spymaster = self._get_current_spymaster(current_color)
            current_operative = self._get_current_operative(current_color)
            if not self._codenames.can_pass():
                clue = current_spymaster.give_clue()
                current_operative.receive_clue(clue)
            elif current_operative.want_pass():
                self._codenames.pass_turn(current_color)
                continue
            guess = current_operative.make_contact()
            self._codenames.guess(guess, current_color)
        return self._codenames.get_winner()


class TestCodenames(unittest.TestCase):

    def setUp(self) -> None:
        self.codenames = Codenames(FILENAME)
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
            codenames = Codenames(FILENAME)
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


if __name__ == '__main__':
    unittest.main()
