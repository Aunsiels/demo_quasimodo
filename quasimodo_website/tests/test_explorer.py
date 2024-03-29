import os
import unittest
from urllib.request import urlopen


from quasimodo_website import DB
from quasimodo_website.models.fact import add_all_facts_to_db, read_facts
from quasimodo_website.models.fact_feedback import FactFeedback
from quasimodo_website.tests.browser_test import BrowserTest

SAMPLE_PATH = os.path.abspath(os.path.dirname(__file__)) +\
              "/quasimodo_sample.tsv"

POLARITY_COLUMN = 4

LOCAL_SIGMA_COLUMN = 7

NEIGHBORHOOD_SIGMA_COLUMN = 6

PLAUSIBILITY_COLUMN = 5

MODALITY_COLUMN = 3

OBJECT_COLUMN = 2

PREDICATE_COLUMN = 1

SUBJECT_COLUMN = 0


class TestExplorer(BrowserTest):

    def setUp(self) -> None:
        self.facts = read_facts(SAMPLE_PATH)
        add_all_facts_to_db(self.facts, DB)

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()
        super().tearDown()

    def test_server_is_up_and_running(self):
        response = urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)

    def test_click_home(self):
        self.browser.get(self.get_server_url() + "/explorer")
        self.browser.find_elements_by_link_text("Home")[0].click()
        self.assertEqual(self.browser.current_url,
                         self.get_server_url() + "/")

    def test_has_table(self):
        self.browser.get(self.get_server_url() + "/explorer")
        table = self.browser.find_elements_by_xpath("//table")
        self.assertEqual(len(table), 1)

    def test_has_rows(self):
        self.browser.get(self.get_server_url() + "/explorer")
        table = self.browser.find_elements_by_xpath("//table//tr")
        self.assertEqual(len(table), 7)

    def test_has_rows_next(self):
        self.browser.get(self.get_server_url() + "/explorer?page=2")
        rows = self.browser.find_elements_by_xpath("//table//tr")
        self.assertEqual(len(rows), 7)

    def test_show_total(self):
        self.browser.get(self.get_server_url() + "/explorer")
        self.assertIn("18", self.browser.page_source)

    def test_get_next_page(self):
        self.browser.get(self.get_server_url() + "/explorer")
        self.assertEqual(
            len(self.browser.find_elements_by_link_text("Previous facts")),
            0)
        self.browser.find_element_by_link_text("Next facts").click()
        rows = self.browser.find_elements_by_xpath("//table//tr")
        self.assertEqual(len(rows), 7)

    def test_get_previous_page(self):
        self.browser.get(self.get_server_url() + "/explorer?page=2")
        self.assertEqual(
            len(self.browser.find_elements_by_link_text("Next facts")),
            1)
        self.browser.find_element_by_link_text("Previous facts").click()
        rows = self.browser.find_elements_by_xpath("//table//tr")
        self.assertEqual(len(rows), 7)

    def test_sorted_pd(self):
        self.browser.get(self.get_server_url() + "/explorer")
        self.check_if_is_sorted_column(PLAUSIBILITY_COLUMN, True)

    def test_sorted_pd_default(self):
        self.browser.get(self.get_server_url() + "/explorer?order=blabla")
        self.check_if_is_sorted_column(PLAUSIBILITY_COLUMN, True)

    def test_sorted_pa(self):
        self.browser.get(self.get_server_url() + "/explorer?order=pa")
        self.check_if_is_sorted_column(PLAUSIBILITY_COLUMN)

    def test_sorted_td(self):
        self.browser.get(self.get_server_url() + "/explorer?order=td")
        self.check_if_is_sorted_column(NEIGHBORHOOD_SIGMA_COLUMN, True)

    def test_sorted_ta(self):
        self.browser.get(self.get_server_url() + "/explorer?order=ta")
        self.check_if_is_sorted_column(NEIGHBORHOOD_SIGMA_COLUMN)

    def test_sorted_sd(self):
        self.browser.get(self.get_server_url() + "/explorer?order=sd")
        self.check_if_is_sorted_column(LOCAL_SIGMA_COLUMN, True)

    def test_sorted_sa(self):
        self.browser.get(self.get_server_url() + "/explorer?order=sa")
        self.check_if_is_sorted_column(LOCAL_SIGMA_COLUMN)

    def check_if_is_sorted_column(self, column_number, reverse=False):
        column_values = self.get_column_values(column_number)
        column_values = [float(x) for x in column_values]
        self.assertEqual(
            column_values,
            sorted(column_values, reverse=reverse))

    def get_column_values(self, column_number):
        rows = self.browser.find_elements_by_xpath("//table//tr")
        column_values = []
        for row in rows:
            tds = row.find_elements_by_tag_name("td")
            if len(tds) == 0:
                continue
            column_values.append(tds[column_number].text)
        return column_values

    def test_search_by_subject(self):
        self.browser.get(self.get_server_url() + "/explorer/search")
        subject = self.browser.find_element_by_name("subject")
        subject.send_keys("snow")
        self.browser.find_element_by_name("search").click()
        subjects_on_page = self.get_column_values(SUBJECT_COLUMN)
        self.assertEqual(set(subjects_on_page), {"snow"})

    def test_search_by_subject_count(self):
        self.browser.get(self.get_server_url() + "/explorer/search")
        subject = self.browser.find_element_by_name("subject")
        subject.send_keys("snow")
        self.browser.find_element_by_name("search").click()
        self.assertIn("1", self.browser.page_source)

    def test_search_by_predicate(self):
        self.browser.get(self.get_server_url() + "/explorer/search")
        subject = self.browser.find_element_by_name("predicate")
        subject.send_keys("make")
        self.browser.find_element_by_name("search").click()
        predicate_on_page = self.get_column_values(PREDICATE_COLUMN)
        self.assertEqual(set(predicate_on_page), {"make"})

    def test_search_by_object(self):
        self.browser.get(self.get_server_url() + "/explorer/search")
        subject = self.browser.find_element_by_name("object")
        subject.send_keys("music")
        self.browser.find_element_by_name("search").click()
        object_on_page = self.get_column_values(OBJECT_COLUMN)
        self.assertEqual(set(object_on_page), {"music"})

    def test_search_by_modality(self):
        self.browser.get(self.get_server_url() + "/explorer/search")
        subject = self.browser.find_element_by_name("modality")
        subject.send_keys("some")
        self.browser.find_element_by_name("search").click()
        modality_on_page = self.get_column_values(MODALITY_COLUMN)
        self.assertTrue(len(modality_on_page) > 0)
        self.assertTrue(all(["some" in x for x in modality_on_page]))

    def test_search_by_polarity_positive(self):
        self.browser.get(self.get_server_url() + "/explorer/search")
        subject = self.browser.find_element_by_name("polarity")
        subject.send_keys("Positive")
        self.browser.find_element_by_name("search").click()
        object_on_page = self.get_column_values(POLARITY_COLUMN)
        self.assertEqual(set(object_on_page), {"POSITIVE"})

    def test_search_by_polarity_negative(self):
        self.browser.get(self.get_server_url() + "/explorer/search")
        subject = self.browser.find_element_by_name("polarity")
        subject.send_keys("Negative")
        self.browser.find_element_by_name("search").click()
        object_on_page = self.get_column_values(POLARITY_COLUMN)
        self.assertEqual(set(object_on_page), {"NEGATIVE"})

    def test_fact_page_no_id(self):
        self.browser.get(self.get_server_url() + "/explorer/fact")
        self.assertEqual(self.browser.current_url,
                         self.get_server_url() + "/")

    def test_fact_page_check_url_correct(self):
        self.browser.get(self.get_server_url() + "/explorer/fact?id=1")
        self.assertEqual(self.browser.current_url,
                         self.get_server_url() + "/explorer/fact?id=1")
        self.assertEqual(self.get_column_values(0)[0], "musician")

    def test_fact_page_check_url_incorrect(self):
        self.browser.get(self.get_server_url() + "/explorer/fact?id=0")
        self.assertEqual(self.browser.current_url,
                         self.get_server_url() + "/")

    def test_give_positive_feedback(self):
        class_polarity = "positive-feedback"
        self.check_give_feedback(class_polarity)

    def test_give_negative_feedback(self):
        class_polarity = "negative-feedback"
        self.check_give_feedback(class_polarity)

    def check_give_feedback(self, type_of_feedback):
        self.browser.get(self.get_server_url() + "/explorer")
        span = self.browser.find_elements_by_xpath("//table//tr//td//span[@class='" + type_of_feedback + "']")[0]
        self.retry_execute_until(
            lambda: self.check_is_displayed(span),
            60)
        span.click()
        self.retry_execute_until(
            lambda: self.browser.switch_to.alert,
            60)
        alert_box = self.browser.switch_to.alert
        self.assertIn("thank", alert_box.text)
        alert_box.accept()
        self.assertEqual(FactFeedback.query.count(), 1)


if __name__ == '__main__':
    unittest.main()
