import os
import time

from flask_testing import LiveServerTestCase
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException

from quasimodo_website import DB, Config, create_app
from quasimodo_website.tests.test_database import DB_TEST_PATH


class WrongUrlException(Exception):
    pass


class NotDisplayedException(Exception):
    pass


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
        DB.session.remove()
        DB.drop_all()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.browser.quit()
        cls.display.stop()
        cls.browser = None
        cls.display = None

    def retry_execute_until(self, action_to_perform, time_limit):
        found_element = False
        time_begin = time.time()
        while time.time() - time_begin < time_limit:
            try:
                action_to_perform()
                found_element = True
                break
            except NoSuchElementException:
                pass
            except WrongUrlException:
                pass
            except NotDisplayedException:
                pass
            except NoAlertPresentException:
                pass
        self.assertTrue(found_element)

    def check_on_url(self, url):
        if self.browser.current_url != url:
            raise WrongUrlException

    @staticmethod
    def check_is_displayed(element):
        if not element.is_displayed():
            raise NotDisplayedException

