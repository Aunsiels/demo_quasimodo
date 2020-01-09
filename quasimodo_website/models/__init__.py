from quasimodo_website import db
from quasimodo_website.models.fact import Fact


def create_all_db():
    db.create_all()
