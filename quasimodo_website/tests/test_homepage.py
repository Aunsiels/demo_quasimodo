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
        test_to_click = "Home"
        final_url = "/"
        self.check_click_text_goes_to(test_to_click, final_url)

    def check_click_text_goes_to(self, test_to_click, final_url):
        self.browser.get(self.get_server_url() + "/")
        self.browser.find_element_by_link_text(test_to_click).click()
        self.assertEqual(self.browser.current_url,
                         self.get_server_url() + final_url)

    def test_click_explorer(self):
        test_to_click = "Explorer"
        final_url = "/explorer/"
        self.check_click_text_goes_to(test_to_click, final_url)


if __name__ == '__main__':
    unittest.main()
