import time
import unittest

from selenium.common.exceptions import NoSuchElementException

from quasimodo_website.tests.test_homepage import TestHomepage

TIME_TO_COLLAPSE = 120


class WrongUrlException(Exception):
    pass


class TestHomepageSmall(TestHomepage):

    def test_click_home(self):
        home_url = self.get_server_url() + "/"
        self.browser.get(home_url)
        self.browser.find_element_by_class_name("navbar-toggler-icon").click()
        self.retry_execute_until(
            lambda: self.browser.find_element_by_link_text("Home"),
            TIME_TO_COLLAPSE)
        self.retry_execute_until(
            lambda: self.browser.find_element_by_link_text("Home").click(),
            TIME_TO_COLLAPSE)
        self.retry_execute_until(
            lambda: self.check_on_url(home_url),
            TIME_TO_COLLAPSE)
        self.assertEqual(self.browser.current_url, home_url)

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
        self.assertTrue(found_element)

    def check_on_url(self, url):
        if self.browser.current_url != url:
            raise WrongUrlException

    def test_click_explorer(self):
        self.browser.get(self.get_server_url() + "/")
        self.browser.find_element_by_class_name("navbar-toggler-icon").click()
        # These tests do not work all the time
        # I guess it comes from a too long loading time
        self.retry_execute_until(
            lambda: self.browser.find_element_by_link_text("Explorer"),
            TIME_TO_COLLAPSE)
        self.retry_execute_until(
            lambda: self.browser.find_element_by_link_text("Explorer").click(),
            TIME_TO_COLLAPSE)
        explorer_url = self.get_server_url() + "/explorer/"
        self.retry_execute_until(
            lambda: self.check_on_url(explorer_url),
            TIME_TO_COLLAPSE)
        self.assertEqual(self.browser.current_url, explorer_url)

    @classmethod
    def setUpClass(cls) -> None:
        cls.start_display(200, 100)
        cls.start_browser()


if __name__ == '__main__':
    unittest.main()
