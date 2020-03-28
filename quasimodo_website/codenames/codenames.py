import json
import random
from enum import Enum, auto

N_CARDS_TO_GUESS = 17
N_CARDS = 25


class Codenames:

    def __init__(self):
        self.words = None
        self.red_cards = None
        self.blue_cards = None
        self.assassin_card = None
        self.red_cards_remaining = None
        self.blue_cards_remaining = None
        self.winner = None
        self.found_assassin = False
        self.has_played_already = False
        self.guessed_words = []
        self.current_player = None

    @classmethod
    def from_filename(cls, filename):
        codenames = Codenames()
        codenames.initialize_from_filename(filename)
        return codenames

    @classmethod
    def from_json(cls, json_s):
        dict_repr = json.loads(json_s)
        codenames = Codenames()
        codenames.initialize_from_dict(dict_repr)
        return codenames

    def to_json(self):
        dict_repr = {
            "words": self.words,
            "red_cards": self.red_cards,
            "blue_cards": self.blue_cards,
            "assassin_card": self.assassin_card,
            "guessed_words": self.guessed_words,
            "has_played_already": self.has_played_already,
            "current_player":
                "RED"
                if self.current_player == CodenameColor.RED
                else "BLUE",
            "winner": self.winner
        }
        return json.dumps(dict_repr)

    def initialize_from_filename(self, filename):
        self._initialize_words(filename)
        self.current_player = random.choice([CodenameColor.RED,
                                             CodenameColor.BLUE])
        self._initialize_color_cards()

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
        self._check_if_can_guess(color)
        self._make_guess(color, word)

    def _make_guess(self, color, word):
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

    def _check_if_can_guess(self, color):
        if self.is_finished():
            raise GameFinishedException
        if self.current_player != color:
            raise NotYourTurnException

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

    def is_valid_clue(self, clue):
        if any((clue.lower() in word.lower()
                or word.lower() in clue.lower()
                for word in self.get_words())):
            return False
        return True

    def initialize_from_dict(self, dict_repr):
        self.words = dict_repr["words"]
        self.red_cards = dict_repr["red_cards"]
        self.blue_cards = dict_repr["blue_cards"]
        self.assassin_card = dict_repr["assassin_card"]
        self.guessed_words = dict_repr["guessed_words"]
        self.has_played_already = dict_repr["has_played_already"]
        self.current_player = \
            CodenameColor.RED\
            if dict_repr["current_player"] == "RED"\
            else CodenameColor.BLUE
        self.winner = dict_repr["winner"]
        self.red_cards_remaining = [x for x in self.red_cards
                                    if x not in self.guessed_words]
        self.blue_cards_remaining = [x for x in self.blue_cards
                                     if x not in self.guessed_words]
        self.found_assassin = self.assassin_card in self.guessed_words


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
