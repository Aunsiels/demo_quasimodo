import json

from quasimodo_website.tests.browser_test import BrowserTest


class TestTaboo(BrowserTest):

    def test_can_access(self):
        self.browser.get(self.get_server_url() + "/taboo")
        self.assertEqual(self.browser.current_url, self.get_server_url() + "/taboo/")

    def test_no_word_given(self):
        self.browser.get(self.get_server_url() + "/taboo/get_given_words")
        words = self.get_json()
        self.assertEqual(0, len(words))

    def test_give_a_word(self):
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=lion")
        self.browser.get(self.get_server_url() + "/taboo/get_given_words")
        words = self.get_json()
        self.assertEqual(["lion"], words)

    def test_give_two_words(self):
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=lion")
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=elephant")
        self.browser.get(self.get_server_url() + "/taboo/get_given_words")
        words = self.get_json()
        self.assertEqual(["lion", "elephant"], words)

    def test_reinitialize(self):
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=lion")
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=elephant")
        self.browser.get(self.get_server_url() + "/taboo")
        self.browser.get(self.get_server_url() + "/taboo/get_given_words")
        words = self.get_json()
        self.assertEqual([], words)

    def get_json(self):
        pre = self.browser.find_element_by_tag_name("pre").text
        words = json.loads(pre)
        return words

    def test_get_word_to_guess(self):
        self.browser.get(self.get_server_url() + "/taboo/initialize")
        self.assertEqual(self.get_json().get("status", ""), "Done")
        self.browser.get(self.get_server_url() + "/taboo")
        self.browser.get(self.get_server_url() + "/taboo/get_word_to_guess")
        word_to_guess = self.get_json().get("word_to_guess", "")
        print(self.get_json())
        self.assertNotEqual(word_to_guess, "")
