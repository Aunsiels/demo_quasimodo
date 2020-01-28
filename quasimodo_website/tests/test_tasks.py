import json

from quasimodo_website.tests.browser_test import BrowserTest


class TestTaboo(BrowserTest):

    def setUp(self) -> None:
        super().setUp()
        self.client = self.app.test_client()

    def test_pipeline_no_subject(self):
        self.assertEqual("Subject not valid", self.client.get("/tasks/run_pipeline").data.decode("utf-8"))

    def test_pipeline_a_subject(self):
        self.assertEqual("1", self.client.get("/tasks/run_pipeline?subject=elephant").data.decode("utf-8"))

    def test_meta_no_job_id(self):
        self.assertEqual({}, json.loads(self.client.get("/tasks/get_meta").data.decode("utf-8")))

    def test_meta_with_job_id(self):
        self.client.get("/tasks/run_pipeline?subject=elephant")
        self.assertEqual([{"step name" : "Assertion Generation","steps" : []}],
                         json.loads(self.client.get("/tasks/get_meta?id=1").data.decode("utf-8")))

    def test_meta_invalid_id(self):
        self.client.get("/tasks/run_pipeline?subject=elephant")
        self.assertEqual({},
                         json.loads(self.client.get("/tasks/get_meta?id=2").data.decode("utf-8")))

    def test_is_complete_no_id(self):
        self.assertEqual("Invalid job ID",
                         self.client.get("/tasks/is_complete").data.decode("utf-8"))

    def test_is_complete_valid_id(self):
        self.client.get("/tasks/run_pipeline?subject=elephant")
        self.assertEqual("True",
                         self.client.get("/tasks/is_complete?id=1").data.decode("utf-8"))

    def test_is_complete_invalid_id(self):
        self.assertEqual("Invalid job ID",
                         self.client.get("/tasks/is_complete?id=1").data.decode("utf-8"))
