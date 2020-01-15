import json

from quasimodo_website.tests.browser_test import BrowserTest


class TestTaboo(BrowserTest):

    def setUp(self) -> None:
        self.browser.get(self.get_server_url() + "/taboo/initialize")
        self.browser.get(self.get_server_url() + "/taboo/start_new_game")

    def test_can_access(self):
        self.browser.get(self.get_server_url() + "/taboo")
        self.assertEqual(self.browser.current_url, self.get_server_url() + "/taboo/")

    def test_no_word_given(self):
        self.browser.get(self.get_server_url() + "/taboo/get_given_words")
        words = self.get_json()
        self.assertEqual(0, len(words))

    def test_give_a_word(self):
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=popopotest")
        self.assertNotIn("error", self.get_json())
        self.browser.get(self.get_server_url() + "/taboo/get_given_words")
        words = self.get_json()
        self.assertEqual(["popopotest"], words)

    def test_give_two_words(self):
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=popopotest")
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=pipapopu")
        self.browser.get(self.get_server_url() + "/taboo/get_given_words")
        words = self.get_json()
        self.assertEqual(["popopotest", "pipapopu"], words)

    def test_reinitialize(self):
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=pipapopu")
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=popopotest")
        self.browser.get(self.get_server_url() + "/taboo/start_new_game")
        self.browser.get(self.get_server_url() + "/taboo/get_given_words")
        words = self.get_json()
        self.assertEqual([], words)

    def get_json(self):
        pre = self.browser.find_element_by_tag_name("pre").text
        words = json.loads(pre)
        return words

    def test_get_word_to_guess(self):
        self.browser.get(self.get_server_url() + "/taboo/start_new_game")
        self.browser.get(self.get_server_url() + "/taboo/get_word_to_guess")
        word_to_guess = self.get_json().get("word_to_guess", "")
        self.assertNotEqual(word_to_guess, "")

    def test_give_word_to_guess(self):
        word_to_guess = self.get_json().get("word_to_guess", "")
        self.browser.get(self.get_server_url() + "/taboo/give_word?word="
                         + word_to_guess)
        error = self.get_json().get("error", None)
        self.assertIsNotNone(error)

    def test_give_forbidden_word(self):
        self.browser.get(self.get_server_url() + "/taboo/get_forbidden_words")
        forbidden_words = self.get_json()["forbidden_words"]
        self.browser.get(self.get_server_url() + "/taboo/give_word?word="
                         + forbidden_words[0])
        error = self.get_json().get("error", None)
        self.assertIsNotNone(error)

    def test_guess_a_word(self):
        self.browser.get(self.get_server_url() + "/taboo/guess_word")
        result = self.get_json()
        self.assertIn("guessed", result)
        self.assertIn("is_correct", result)

    def test_guess_a_word_with_a_suggestion(self):
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=music")
        self.browser.get(self.get_server_url() + "/taboo/guess_word")
        result = self.get_json()
        self.assertIn("guessed", result)
        self.assertIn("is_correct", result)