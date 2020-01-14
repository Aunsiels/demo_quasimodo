import os

from flask_testing import LiveServerTestCase
from pyvirtualdisplay import Display
from selenium import webdriver

from quasimodo_website import create_app, Config

DB_TEST_PATH = 'sqlite:///' + os.path.abspath(os.path.dirname(__file__)) +\
               "app_test.db"


class BrowserTest(LiveServerTestCase):

    display = None
    browser = None

    def create_app(self):
        Config.SQLALCHEMY_DATABASE_URI = DB_TEST_PATH
        Config.FACTS_PER_PAGE = 6
        app = create_app(True)
        self.client = app.test_client()
        return app

    @classmethod
    def start_display(cls, width, height):
        cls.display = Display(visible=0, size=(width, height))
        cls.display.start()

    @classmethod
    def start_browser(cls):
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
        cls.browser.quit()
        cls.display.stop()