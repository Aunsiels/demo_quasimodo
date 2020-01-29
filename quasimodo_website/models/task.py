import redis
import rq
from flask import current_app
from datetime import datetime

from quasimodo_website import DB


TEST_JOBS = dict()
COUNTER = 1


# From https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xxii-background-jobs
class JobTest(object):
    meta = [
        {
            "step name" : "Assertion Generation",
            "steps" : []
        }
    ]
    is_finished = True
    is_failed = False
    next_meta = None

    def __init__(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def update(self, next_meta):
        self.next_meta = next_meta

    def refresh(self):
        if self.next_meta is not None:
            self.meta = self.next_meta

    def remove(self):
        global TEST_JOBS
        del TEST_JOBS[self.id]


class Task(DB.Model):
    id = DB.Column(DB.String(36), primary_key=True)
    subject = DB.Column(DB.String(256), nullable=False)
    complete = DB.Column(DB.Boolean, default=False)
    created_on = DB.Column(DB.DateTime, default=datetime.utcnow)

    def get_rq_job(self):
        if not current_app.config["TESTING"]:
            try:
                rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
            except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
                return None
            return rq_job
        else:
            return TEST_JOBS.get(self.id, None)

    def get_meta(self):
        job = self.get_rq_job()
        if job is not None:
            job.refresh()
            return job.meta
        else:
            return {}

    def is_complete(self):
        if not self.complete:
            job = self.get_rq_job()
            if job is None or job.is_finished or job.is_failed:
                self.complete = True
                DB.session.commit()
        return self.complete

    @staticmethod
    def add_task_for_subject(subject):
        if not current_app.config["TESTING"]:
            job = current_app.task_queue.enqueue('run_for_subject.run_for_subject', args=(subject,), timeout=500000)
        else:
            global COUNTER
            job = JobTest(str(COUNTER))
            TEST_JOBS[str(COUNTER)] = job
            COUNTER += 1
        task = Task(id=job.get_id(), subject=subject, complete=False)
        DB.session.add(task)
        DB.session.commit()
        return job.get_id()

