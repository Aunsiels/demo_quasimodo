import urllib.request
import zipfile

from flask import render_template, url_for, current_app
from werkzeug.utils import redirect

from demo import db
from demo.homepage import bp
from demo.models import Fact
from demo.models.fact import read_facts_from_file, add_all_facts_to_db


@bp.route("/")
def home():
    return render_template("homepage.html")


@bp.route("/initialize")
def initialize():
    n_facts = Fact.query.count()
    if n_facts == 0:
        current_app.logger.info("Downloading Quasimodo...")
        url = 'https://www.mpi-inf.mpg.de/fileadmin/inf/d5/research/quasimodo/quasimodo-v1.2.zip'
        file_handle, _ = urllib.request.urlretrieve(url)
        current_app.logger.info("Unzipping Quasimodo...")
        zip_file_object = zipfile.ZipFile(file_handle, 'r')
        first_file = zip_file_object.namelist()[0]
        file = zip_file_object.open(first_file, 'r')
        current_app.logger.info("Reading facts...")
        facts = read_facts_from_file(file)
        current_app.logger.info("Filling database...")
        add_all_facts_to_db(facts, db)
        return "Initialization done"
    return redirect(url_for("homepage.home"))
