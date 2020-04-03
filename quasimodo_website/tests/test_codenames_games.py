import unittest

from quasimodo_website.codenames.codenames import Codenames, CodenameColor
from quasimodo_website.codenames.codenames_agents import CodenamesMaster
from quasimodo_website.codenames.word_vector_players import \
    WordVectorOperative, WordVectorSpyMaster
from quasimodo_website.tests.test_codenames import FILENAME


class TestCodenamesGames(unittest.TestCase):

    def setUp(self) -> None:
        self.codenames = Codenames.from_filename(FILENAME)

    def test_one_vector_player(self):
        game_master = CodenamesMaster(
            self.codenames,
            red_operative=WordVectorOperative(self.codenames,
                                              CodenameColor.RED))
        self.assertIsNotNone(game_master.run_game())

    def test_two_vector_players(self):
        game_master = CodenamesMaster(
            self.codenames,
            red_spymaster=WordVectorSpyMaster(self.codenames,
                                              CodenameColor.RED),
            red_operative=WordVectorOperative(self.codenames,
                                              CodenameColor.RED))
        self.assertIsNotNone(game_master.run_game())


if __name__ == '__main__':
    unittest.main()
