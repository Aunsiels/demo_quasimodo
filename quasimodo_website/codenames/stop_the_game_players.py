from quasimodo_website.codenames.codenames_agents import SpyMaster, Operative
from quasimodo_website.codenames.quasimodo_players import QuasimodoSpyMaster
from quasimodo_website.codenames.word_vector_players import WordVectorSpyMaster


class ClueGivenException(Exception):

    def __init__(self, clue):
        super().__init__()
        self.clue = clue


class StopTheGameOperative(Operative):

    def __init__(self, codenames, color, word_to_guess, want_to_pass):
        super().__init__(codenames, color)
        self.word_to_guess = word_to_guess
        self.want_to_pass = want_to_pass

    def make_contact(self):
        if self.word_to_guess is not None:
            res = self.word_to_guess
            self.word_to_guess = None
            return res
        raise WaitForActionException

    def receive_clue(self, clue):
        if self.word_to_guess is None:
            raise ClueGivenException(clue)

    def want_pass(self):
        if self.want_to_pass is not None:
            res = self.want_to_pass
            self.want_to_pass = None
            return res
        raise WaitForActionException


class WordVectorSpyMasterWhenStopping(WordVectorSpyMaster):

    def __init__(self, codenames, color, word_given=None):
        super().__init__(codenames, color)
        self.word_given = word_given

    def give_clue(self):
        if self.word_given is not None:
            res = self.word_given
            self.word_given = None
            return res
        return super().give_clue()


class QuasimodoSpyMasterWhenStopping(QuasimodoSpyMaster):

    def __init__(self, codenames, color, word_given=None):
        super().__init__(codenames, color)
        self.word_given = word_given

    def give_clue(self):
        if self.word_given is not None:
            res = self.word_given
            self.word_given = None
            return res
        return super().give_clue()


class WaitForActionException(Exception):
    pass


class StopTheGameSpyMaster(SpyMaster):

    def __init__(self, codenames, color, word_to_give):
        super().__init__(codenames, color)
        self.word_to_give = word_to_give

    def give_clue(self):
        if self.word_to_give is not None:
            res = self.word_to_give
            self.word_to_give = None
            return res
        raise WaitForActionException
