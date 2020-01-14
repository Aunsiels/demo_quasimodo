import unittest
from urllib.request import urlopen

from quasimodo_website.tests.browser_test import BrowserTest


class TestHomepage(BrowserTest):

    def test_server_is_up_and_running(self):
        response = urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)

    def test_title(self):
        self.browser.get(self.get_server_url() + "/")
        self.assertTrue("quasimodo" in self.browser.title.lower())

    def test_click_home(self):
        self.browser.get(self.get_server_url() + "/")
        self.browser.find_element_by_link_text("Home").click()
        self.assertEqual(self.browser.current_url, self.get_server_url() + "/")

    def test_click_explorer(self):
        self.browser.get(self.get_server_url() + "/")
        self.browser.find_element_by_link_text("Explorer").click()
        self.assertEqual(self.browser.current_url, self.get_server_url() + "/explorer/")


if __name__ == '__main__':
    unittest.main()
