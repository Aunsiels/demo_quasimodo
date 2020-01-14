import time
import unittest

from quasimodo_website.tests.test_homepage import TestHomepage

TIME_TO_COLLAPSE = 5


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
        cls.start_display(200, 100)
        cls.start_browser()


if __name__ == '__main__':
    unittest.main()
