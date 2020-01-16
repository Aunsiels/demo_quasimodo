import unittest

from quasimodo_website.tests.test_homepage import TestHomepage

TIME_TO_COLLAPSE = 120


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
