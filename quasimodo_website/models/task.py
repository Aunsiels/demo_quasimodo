import redis
import rq
from flask import current_app

from quasimodo_website import DB


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

    def get_id(self):
        return 1


class Task(DB.Model):
    id = DB.Column(DB.String(36), primary_key=True)
    subject = DB.Column(DB.String(256), nullable=False)
    complete = DB.Column(DB.Boolean, default=False)

    def get_rq_job(self):
        if not current_app.config["TESTING"]:
            try:
                rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
            except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
                return None
            return rq_job
        else:
            return JobTest()

    def get_meta(self):
        job = self.get_rq_job()
        if job is not None:
            return job.meta
        else:
            return {}

    def is_complete(self):
        if not self.complete:
            job = self.get_rq_job()
            if job.is_finished or job.is_failed:
                self.complete = True
                DB.session.commit()
        return self.complete

    @staticmethod
    def add_task_for_subject(subject):
        if not current_app.config["TESTING"]:
            job = current_app.task_queue.enqueue('run_for_subject.run_for_subject', args=(subject,), timeout=500000)
        else:
            job = JobTest()
        task = Task(id=job.get_id(), subject=subject, complete=False)
        DB.session.add(task)
        DB.session.commit()
        return job.get_id()

