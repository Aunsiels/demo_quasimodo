import json

from quasimodo_website.models.task import Task
from quasimodo_website.tests.browser_test import BrowserTest


class TestTaboo(BrowserTest):

    def setUp(self) -> None:
        super().setUp()
        self.client = self.app.test_client()

    def test_pipeline_no_subject(self):
        self.assertEqual("Subject not valid", self.client.get("/tasks/run_pipeline").data.decode("utf-8"))

    def test_pipeline_a_subject(self):
        self.assertNotEqual("Subject not valid", self.client.get("/tasks/run_pipeline?subject=elephant").data.decode("utf-8"))

    def test_meta_no_job_id(self):
        self.assertEqual({}, json.loads(self.client.get("/tasks/get_meta").data.decode("utf-8")))

    def test_meta_with_job_id(self):
        self.client.get("/tasks/run_pipeline?subject=elephant")
        self.assertEqual({},
                         json.loads(self.client.get("/tasks/get_meta?id=1").data.decode("utf-8")))

    def test_meta_reload(self):
        id = self.client.get("/tasks/run_pipeline?subject=elephant").data.decode("utf-8").strip()
        Task.query.get(id).get_rq_job().update([{"step name": "Assertion Generation", "steps": []}])
        self.assertEqual([{"step name": "Assertion Generation", "steps": []}],
                         json.loads(self.client.get("/tasks/get_meta?id=" + id).data.decode("utf-8")))

    def test_meta_invalid_id(self):
        self.client.get("/tasks/run_pipeline?subject=elephant").data.decode("utf-8").strip()
        self.assertEqual({},
                         json.loads(self.client.get("/tasks/get_meta?id=654654").data.decode("utf-8")))

    def test_is_complete_no_id(self):
        self.assertEqual("Invalid job ID",
                         self.client.get("/tasks/is_complete").data.decode("utf-8"))

    def test_is_complete_valid_id(self):
        id = self.client.get("/tasks/run_pipeline?subject=elephant").data.decode("utf-8")
        self.assertEqual("True",
                         self.client.get("/tasks/is_complete?id=" + id).data.decode("utf-8"))

    def test_is_complete_invalid_id(self):
        self.assertEqual("Invalid job ID",
                         self.client.get("/tasks/is_complete?id=1").data.decode("utf-8"))

    def test_is_complete_after_remove(self):
        id = self.client.get("/tasks/run_pipeline?subject=elephant").data.decode("utf-8").strip()
        Task.query.get(id).get_rq_job().remove()
        self.assertEqual("True",
                         self.client.get("/tasks/is_complete?id=" + id).data.decode("utf-8"))

    def test_get_all_tasks(self):
        self.client.get("/tasks/run_pipeline?subject=elephant")
        self.browser.get(self.get_server_url() + "/")
