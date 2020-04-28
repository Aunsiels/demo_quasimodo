import json
import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

from quasimodo_website import DB
from quasimodo_website.models.fact import read_facts, add_all_facts_to_db
from quasimodo_website.tests.browser_test import BrowserTest
from quasimodo_website.tests.test_explorer import SAMPLE_PATH

TIME_TO_LOAD = 60


class TestTaboo(BrowserTest):

    def setUp(self) -> None:
        self.facts = read_facts(SAMPLE_PATH)
        add_all_facts_to_db(self.facts, DB)
        self.browser.get(self.get_server_url() + "/taboo/initialize")
        self.browser.get(self.get_server_url() + "/taboo/start_new_game")
        self.client = self.app.test_client()

    def test_can_access(self):
        self.browser.get(self.get_server_url() + "/taboo")
        self.assertEqual(self.browser.current_url,
                         self.get_server_url() + "/taboo/")

    def test_no_word_given(self):
        self.browser.get(self.get_server_url() + "/taboo/get_given_words")
        words = self.get_json()
        self.assertEqual(0, len(words))

    def test_give_a_word(self):
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=zzzz")
        self.assertNotIn("error", self.get_json())
        self.browser.get(self.get_server_url() + "/taboo/get_given_words")
        words = self.get_json()
        self.assertEqual(["zzzz"], words)

    def test_give_two_words(self):
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=ztzt")
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=tztz")
        self.browser.get(self.get_server_url() + "/taboo/get_given_words")
        words = self.get_json()
        self.assertEqual(["ztzt", "tztz"], words)

    def test_reinitialize(self):
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=tztz")
        self.browser.get(self.get_server_url() + "/taboo/give_word?word=ztzt")
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

    def test_getting_wrongly_guessed_words(self):
        self.browser.get(self.get_server_url() + "/taboo/get_wrongly_guessed")
        result = self.get_json()
        self.assertEqual(0, len(result))
        self.browser.get(self.get_server_url() + "/taboo/guess_word")
        self.browser.get(self.get_server_url() + "/taboo/get_wrongly_guessed")
        result = self.get_json()
        self.assertLess(0, len(result))

    def test_reinitialized_wrongly_guessed_words(self):
        self.browser.get(self.get_server_url() + "/taboo/guess_word")
        self.browser.get(self.get_server_url() + "/taboo/start_new_game")
        self.browser.get(self.get_server_url() + "/taboo/get_wrongly_guessed")
        result = self.get_json()
        self.assertEqual(0, len(result))

    def test_before_new_game(self):
        self.browser.get(self.get_server_url() + "/taboo")
        button = self.browser.find_elements_by_id("new-game")
        self.assertEqual(len(button), 1)
        self.assertFalse(self.browser.find_element_by_id("tabooCard")
                                     .is_displayed())

    def test_after_new_game(self):
        self.browser.get(self.get_server_url() + "/taboo")
        self.browser.find_element_by_id("new-game").click()
        self.assertTrue(self.browser.find_element_by_id("tabooCard")
                                    .is_displayed())
        card_header = self.get_card_header()
        self.assertIsNotNone(card_header)
        forbidden_words = self.browser.find_elements_by_xpath(
            "//ul[@id='forbidden_words']/li")
        self.assertEqual(len(forbidden_words), 5)

    def get_card_header(self):
        card_header = self.browser.find_element_by_id("card_title")
        return card_header

    def test_write_something_in_chat(self):
        self.browser.get(self.get_server_url() + "/taboo")
        text_written = 'Test write'
        self.write_message_in_chat(text_written)
        chat = self.get_chat()
        self.assertIn(text_written, chat[-1])

    def write_message_in_chat(self, text_written):
        input_text = self.browser.find_element_by_xpath("//input[@class='mytext']")
        input_text.send_keys(text_written)
        input_text.send_keys(Keys.ENTER)

    def get_chat(self):
        counter = 0
        while counter < 10:
            try:
                messages_li = self.browser.find_elements_by_xpath("//ul[@id='chat-list']//li")
                chat = [message.text for message in messages_li]
                break
            except StaleElementReferenceException:
                time.sleep(1)
                counter += 1
        return chat

    def test_give_in_chat_word_to_guess(self):
        self.browser.get(self.get_server_url() + "/taboo")
        self.browser.find_element_by_id("new-game").click()
        word_to_guess = self.get_card_header().text
        self.write_message_in_chat(word_to_guess)
        chat = self.get_chat()
        self.assertIn("The given word is too similar to the word to guess",
                      chat[-1])

    def test_generate_taboo_card(self):
        self.browser.get(self.get_server_url() +\
                         "/taboo/generate_card?subject=musician&n_words=2"
                         "&format=json")
        objects = self.get_json()
        self.assertEqual(len(objects), 2)