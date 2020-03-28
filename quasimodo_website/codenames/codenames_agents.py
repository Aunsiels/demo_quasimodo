import collections

from quasimodo_website.codenames.codenames import CodenameColor

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
            return self._blue_operative
        else:
            return self._red_operative

    def run_game(self):
        """
        Run the game and return the winner
        :return: The winning team color
        """
        counter = 1
        while not self._codenames.is_finished():
            print("Turn", counter)
            counter += 1
            current_color = self._codenames.get_current_player()
            print(current_color, "is playing...")
            current_spymaster = self._get_current_spymaster(current_color)
            current_operative = self._get_current_operative(current_color)
            if not self._codenames.can_pass():
                clue = current_spymaster.give_clue()
                if not self._codenames.is_valid_clue(clue.word):
                    print("Invalid clue!")
                    self._codenames.guess("a", current_color)
                    continue
                current_operative.receive_clue(clue)
            elif current_operative.want_pass():
                self._codenames.pass_turn(current_color)
                continue
            guess = current_operative.make_contact()
            self._codenames.guess(guess, current_color)
        print(len(self._codenames.get_remaining_words_by_color(
            CodenameColor.RED
        )))
        print(len(self._codenames.get_remaining_words_by_color(
            CodenameColor.BLUE
        )))
        return self._codenames.get_winner()