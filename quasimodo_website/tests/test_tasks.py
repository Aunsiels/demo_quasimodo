import json
import os

import requests
from flask import url_for

from quasimodo_website.tests.browser_test import BrowserTest


class TestTaboo(BrowserTest):

    def setUp(self) -> None:
        super().setUp()
        self.client = self.app.test_client()

    def test_pipeline_no_subject(self):
        self.assertEqual(
            "Subject not valid",
            self.client.get("/tasks/run_pipeline").data.decode("utf-8"))

    def test_pipeline_a_subject(self):
        raw_page = self.client.get("/tasks/run_pipeline?subject=elephant")
        self.assertNotEqual(
            "Subject not valid",
            raw_page.data.decode("utf-8"))

    def test_meta_no_job_id(self):
        self.assertTrue(
            self.client.get("/tasks/get_meta").location.endswith("/tasks/"))

    def test_meta_with_job_id(self):
        raw_page = self.client.get("/tasks/run_pipeline?subject=elephant")
        id = raw_page.data.decode("utf-8")
        url_meta = url_for("tasks.get_meta", id=id, format="json")
        raw_page = self.client.get(url_meta)
        self.assertEqual(
            {},
            json.loads(raw_page.data.decode("utf-8")))

    def test_meta_reload(self):
        raw_data = self.client.get("/tasks/run_pipeline?subject=elephant")
        id = raw_data.data.decode("utf-8").strip()
        meta = [{"step name": "Assertion Generation", "steps": []}]
        self.client.post(url_for("tasks.set_meta", id=id), json=meta)
        url_meta = url_for("tasks.get_meta", id=id, format="json")
        raw_page = self.client.get(url_meta)
        self.assertEqual(
            [{"step name": "Assertion Generation", "steps": []}],
            json.loads(raw_page.data.decode("utf-8")))

    def test_meta_reload_big(self):
        url_run = self.get_server_url() + \
                  "/tasks/run_pipeline?subject=elephant"
        self.browser.get(url_run)
        id = self.browser.page_source\
            .replace("<html><head></head><body>", "")\
            .replace("</body></html>", "").strip()
        path_meta = os.path.dirname(os.path.realpath(__file__)) + "/meta.json"
        meta = json.load(open(path_meta))
        url_set = self.get_server_url() + url_for("tasks.set_meta", id=id)
        requests.post(url_set, json=meta)
        url_meta = self.get_server_url() + url_for("tasks.get_meta", id=id)
        self.browser.get(url_meta)
        self.assertNotIn("Internal Server Error", self.browser.page_source)

    def test_meta_invalid_id(self):
        self.client.get("/tasks/run_pipeline?subject=elephant")
        raw_page = self.client.get("/tasks/get_meta?id=654654")
        self.assertTrue(raw_page.location.endswith("/tasks/"))

    def test_is_complete_no_id(self):
        raw_page = self.client.get("/tasks/is_complete")
        self.assertEqual("Invalid job ID",
                         raw_page.data.decode("utf-8"))

    def test_is_complete_valid_id(self):
        raw_page = self.client.get("/tasks/run_pipeline?subject=elephant")
        id = raw_page.data.decode("utf-8")
        raw_page = self.client.get("/tasks/is_complete?id=" + id)
        self.assertEqual("True",
                         raw_page.data.decode("utf-8"))

    def test_is_complete_invalid_id(self):
        raw_page = self.client.get("/tasks/is_complete?id=1")
        self.assertEqual("Invalid job ID",
                         raw_page.data.decode("utf-8"))

    def test_is_complete_after_remove(self):
        raw_page = self.client.get("/tasks/run_pipeline?subject=elephant")
        id = raw_page.data.decode("utf-8").strip()
        self.client.get(url_for("tasks.remove", id=id))
        raw_page = self.client.get("/tasks/is_complete?id=" + id)
        is_complete = raw_page.data.decode("utf-8")
        self.assertEqual("True", is_complete)

    def test_get_all_tasks(self):
        self.client.get("/tasks/run_pipeline?subject=elephant")
        self.browser.get(self.get_server_url() + "/")
