import os
import unittest

import pytest
from flask import current_app

from quasimodo_website import db
from quasimodo_website.models.fact import read_facts, Fact, add_all_facts_to_db

DB_TEST_PATH = 'sqlite:///' + os.path.abspath(os.path.dirname(__file__)) +\
               "/app_test.db"

PATH_TO_SAMPLE = os.path.abspath(os.path.dirname(__file__)) +\
                 "/quasimodo_sample.tsv"


@pytest.mark.usefixtures('live_server')
class TestDatabase(unittest.TestCase):

    def setUp(self) -> None:
        self.facts = read_facts(PATH_TO_SAMPLE)
        self.first_fact = self.facts[0]

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_read_quasimodo(self):
        self.assertEqual(len(self.facts), 10)

    def test_contains_subject(self):
        self.assertEqual(self.first_fact.subject, "musician")

    def test_contains_predicate(self):
        self.assertEqual(self.first_fact.predicate, "make")

    def test_contains_object(self):
        self.assertEqual(self.first_fact.object, "music")

    def test_contains_modality(self):
        self.assertEqual(self.first_fact.modality, [])

    def test_contains_negativity(self):
        self.assertFalse(self.first_fact.is_negative)

    def test_contains_plausibility(self):
        self.assertAlmostEqual(self.first_fact.plausibility, 1.0, 1)

    def test_contains_typicality(self):
        self.assertAlmostEqual(self.first_fact.typicality, 0.0, 1)

    def test_contains_saliency(self):
        self.assertAlmostEqual(self.first_fact.saliency, 0.0, 1)

    def test_contains_examples(self):
        self.assertEqual(len(self.first_fact.examples), 2)

    def test_contains_examples_json(self):
        self.assertTrue(isinstance(self.first_fact.examples_json, str))

    def test_examples_have_text(self):
        self.assertEqual(self.first_fact.examples[0][0],
                         "musicians make music")

    def test_examples_have_occurrences(self):
        self.assertEqual(self.first_fact.examples[0][1], 12)

    def test_add_database(self):
        db.session.add(self.first_fact)
        db.session.commit()
        self.assertEqual(len(Fact.query.all()), 1)

    def test_add_all_database(self):
        add_all_facts_to_db(self.facts, db)
        self.assertEqual(len(Fact.query.all()), 10)

    def test_paginate(self):
        add_all_facts_to_db(self.facts, db)
        current_app.config["FACTS_PER_PAGE"] = 5
        self.assertEqual(
            len(Fact.query.paginate(1,
                                    current_app.config["FACTS_PER_PAGE"],
                                    False).items),
            5)


if __name__ == '__main__':
    unittest.main()
