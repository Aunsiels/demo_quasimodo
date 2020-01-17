import unittest

from quasimodo_website.tests.test_homepage import TestHomepage

TIME_TO_COLLAPSE = 120


class TestHomepageSmall(TestHomepage):

    def check_click_text_goes_to(self, text_to_click, final_url):
        self.browser.get(self.get_server_url() + "/")
        self.browser.find_element_by_class_name("navbar-toggler-icon").click()
        # These tests do not work all the time
        # I guess it comes from a too long loading time
        self.retry_execute_until(
            lambda: self.browser.find_element_by_link_text(text_to_click),
            TIME_TO_COLLAPSE)
        self.retry_execute_until(
            lambda: self.browser.find_element_by_link_text(text_to_click)
                .click(),
            TIME_TO_COLLAPSE)
        explorer_url = self.get_server_url() + final_url
        self.retry_execute_until(
            lambda: self.check_on_url(explorer_url),
            TIME_TO_COLLAPSE)
        self.assertEqual(self.browser.current_url, explorer_url)

    @classmethod
    def setUpClass(cls) -> None:
        cls.start_display(200, 400)
        cls.start_browser()


if __name__ == '__main__':
    unittest.main()
