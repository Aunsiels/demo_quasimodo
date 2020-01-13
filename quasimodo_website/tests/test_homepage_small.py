import time
import unittest
import os

from selenium import webdriver
from pyvirtualdisplay import Display

from quasimodo_website.tests.test_homepage import TestHomepage

TIME_TO_COLLAPSE = 1


class TestHomepageSmall(TestHomepage):

    def test_click_home(self):
        self.browser.get(self.get_server_url() + "/")
        self.browser.find_element_by_class_name("navbar-toggler-icon").click()
        time.sleep(TIME_TO_COLLAPSE)
        self.browser.find_element_by_link_text("Home").click()
        self.assertEqual(self.browser.current_url, self.get_server_url() + "/")

    def test_click_explorer(self):
        self.browser.get(self.get_server_url() + "/")
        self.browser.find_element_by_class_name("navbar-toggler-icon").click()
        time.sleep(1)
        self.browser.find_element_by_link_text("Explorer").click()
        self.assertEqual(self.browser.current_url, self.get_server_url() + "/explorer/")

    @classmethod
    def setUpClass(cls) -> None:
        cls.display = Display(visible=0, size=(200,100))
        cls.display.start()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')

        chrome_options.add_experimental_option('prefs', {
            'download.default_directory': os.getcwd(),
            'download.prompt_for_download': False,
        })
        cls.browser = webdriver.Chrome(chrome_options=chrome_options)


if __name__ == '__main__':
    unittest.main()
