from flask import request, current_app, jsonify

from quasimodo_website.models.task import Task
from quasimodo_website.tasks.blueprint import BP


@BP.route("/run_pipeline")
def run_pipeline():
    subject = request.args.get('subject', None, type=str)
    if subject is not None:
        current_app.logger.info("Pipeline for: " + subject)
        return str(Task.add_task_for_subject(subject))
    return "Subject not valid"


@BP.route("/get_meta")
def get_meta():
    job_id = request.args.get("id", None, type=str)
    if job_id is None:
        return jsonify({})
    task = Task.query.get(job_id)
    if task is not None:
        return jsonify(task.get_meta())
    return jsonify({})


@BP.route("/is_complete")
def is_complete():
    job_id = request.args.get("id", None, type=str)
    if job_id is None:
        return "Invalid job ID"
    task = Task.query.get(job_id)
    if task is None:
        return "Invalid job ID"
    return str(task.is_complete())
