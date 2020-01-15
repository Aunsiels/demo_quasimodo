import os

from flask_testing import LiveServerTestCase
from pyvirtualdisplay import Display
from selenium import webdriver

from quasimodo_website import db, Config, create_app
from quasimodo_website.tests.test_database import DB_TEST_PATH


class BrowserTest(LiveServerTestCase):

    def create_app(self):
        Config.SQLALCHEMY_DATABASE_URI = DB_TEST_PATH
        Config.FACTS_PER_PAGE = 6
        app = create_app(True)
        return app

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
        db.session.remove()
        db.drop_all()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.browser.quit()
        cls.display.stop()
        print("Close browser")
        cls.browser = None
        cls.display = None
