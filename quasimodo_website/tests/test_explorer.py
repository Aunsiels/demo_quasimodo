import os
import unittest
from urllib.request import urlopen

from quasimodo_website import db
from quasimodo_website.models.fact import add_all_facts_to_db, read_facts
from quasimodo_website.tests.browser_test import BrowserTest

SAMPLE_PATH = os.path.abspath(os.path.dirname(__file__)) + "/quasimodo_sample.tsv"

POLARITY_COLUMN = 4

SALIENCY_COLUMN = 7

TYPICALITY_COLUMN = 6

PLAUSIBILITY_COLUMN = 5

MODALITY_COLUMN = 3

OBJECT_COLUMN = 2

PREDICATE_COLUMN = 1

SUBJECT_COLUMN = 0


class TestExplorer(BrowserTest):

    def setUp(self) -> None:
        self.facts = read_facts(SAMPLE_PATH)
        add_all_facts_to_db(self.facts, db)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
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
        self.assertEqual(len(rows), 5)

    def test_get_next_page(self):
        self.browser.get(self.get_server_url() + "/explorer")
        self.assertEqual(
            len(self.browser.find_elements_by_link_text("Previous facts")),
            0)
        self.browser.find_element_by_link_text("Next facts").click()
        rows = self.browser.find_elements_by_xpath("//table//tr")
        self.assertEqual(len(rows), 5)

    def test_get_previous_page(self):
        self.browser.get(self.get_server_url() + "/explorer?page=2")
        self.assertEqual(
            len(self.browser.find_elements_by_link_text("Next facts")),
            0)
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
        self.check_if_is_sorted_column(TYPICALITY_COLUMN, True)

    def test_sorted_ta(self):
        self.browser.get(self.get_server_url() + "/explorer?order=ta")
        self.check_if_is_sorted_column(TYPICALITY_COLUMN)

    def test_sorted_sd(self):
        self.browser.get(self.get_server_url() + "/explorer?order=sd")
        self.check_if_is_sorted_column(SALIENCY_COLUMN, True)

    def test_sorted_sa(self):
        self.browser.get(self.get_server_url() + "/explorer?order=sa")
        self.check_if_is_sorted_column(SALIENCY_COLUMN)

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


if __name__ == '__main__':
    unittest.main()
