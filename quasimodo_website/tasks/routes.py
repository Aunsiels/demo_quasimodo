from flask import request, current_app, jsonify, url_for, render_template

from quasimodo_website.models.task import Task
from quasimodo_website.tasks.blueprint import BP


@BP.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    tasks = Task.query.paginate(page, current_app.config["FACTS_PER_PAGE"], False)
    next_url = url_for('explorer.home', page=tasks.next_num) if tasks.has_next else None
    prev_url = url_for('explorer.home', page=tasks.prev_num) if tasks.has_prev else None
    return render_template("tasks_list.html", facts=tasks.items,
                           next_url=next_url,
                           prev_url=prev_url)


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
