import unittest
from urllib.request import urlopen

from flask_testing import LiveServerTestCase

from demo import create_app

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from pyvirtualdisplay import Display


class TestHomepage(LiveServerTestCase):

    browser = None
    display = None

    def create_app(self):
        app = create_app(True)
        self.client = app.test_client()
        return app

    def test_server_is_up_and_running(self):
        response = urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)

    def test_title(self):
        self.browser.get(self.get_server_url() + "/")
        self.assertTrue("quasimodo" in self.browser.title.lower())

    def test_click_home(self):
        self.browser.get(self.get_server_url() + "/")
        self.browser.find_elements_by_link_text("Home")[0].click()
        self.assertEqual(self.browser.current_url, self.get_server_url() + "/")

    def test_click_explorer(self):
        self.browser.get(self.get_server_url() + "/")
        self.browser.find_elements_by_link_text("Explorer")[0].click()
        self.assertEqual(self.browser.current_url, self.get_server_url() + "/explorer/")

    @classmethod
    def setUpClass(cls) -> None:
        cls.display = Display(visible=0, size=(800, 600))
        cls.display.start()
        options = Options()
        options.headless = True
        cls.browser = webdriver.Firefox(options=options)

    def tearDown(self) -> None:
        self.browser.delete_all_cookies()

    @classmethod
    def tearDownClass(cls) -> None:
       cls.browser.quit()
       cls.display.stop()


if __name__ == '__main__':
    unittest.main()
