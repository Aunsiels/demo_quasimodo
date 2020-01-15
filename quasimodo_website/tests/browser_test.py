import os
import unittest

import pytest
from flask import url_for
from pyvirtualdisplay import Display
from selenium import webdriver


@pytest.mark.usefixtures('live_server')
class BrowserTest(unittest.TestCase):

    @staticmethod
    def get_server_url():
        return url_for('homepage.home', _external=True).strip("/")

    display = None
    browser = None

    @classmethod
    def start_display(cls, width, height):
        cls.display = Display(visible=0, size=(width, height))
        cls.display.start()

    @classmethod
    def start_browser(cls):
        print("Start Browser")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_experimental_option('prefs', {
            'download.default_directory': os.getcwd(),
            'download.prompt_for_download': False,
        })
        cls.browser = webdriver.Chrome(chrome_options=chrome_options)

    @classmethod
    def setUpClass(cls) -> None:
        cls.start_display(1600, 1024)
        cls.start_browser()

    def tearDown(self) -> None:
        self.browser.delete_all_cookies()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.browser.quit()
        cls.display.stop()
        print("Close browser")
        cls.browser = None
        cls.display = None
