import time
import unittest

from selenium.common.exceptions import NoSuchElementException

from quasimodo_website.tests.test_homepage import TestHomepage

TIME_TO_COLLAPSE = 20


class TestHomepageSmall(TestHomepage):

    def test_click_home(self):
        self.browser.get(self.get_server_url() + "/")
        self.browser.find_element_by_class_name("navbar-toggler-icon").click()
        self.retry_execute_until(
            lambda: self.browser.find_element_by_link_text("Home").click(),
            TIME_TO_COLLAPSE)
        self.assertEqual(self.browser.current_url, self.get_server_url() + "/")

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
        self.assertTrue(found_element)

    def test_click_explorer(self):
        self.browser.get(self.get_server_url() + "/")
        self.browser.find_element_by_class_name("navbar-toggler-icon").click()
        self.retry_execute_until(
            lambda: self.browser.find_element_by_link_text("Explorer").click(),
            TIME_TO_COLLAPSE)
        self.assertEqual(self.browser.current_url, self.get_server_url() + "/explorer/")

    @classmethod
    def setUpClass(cls) -> None:
        cls.start_display(200, 100)
        cls.start_browser()


if __name__ == '__main__':
    unittest.main()
