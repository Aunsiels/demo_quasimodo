from quasimodo_website.database import DB
from quasimodo_website.models.fact import Fact


def create_all_db():
    DB.create_all()
