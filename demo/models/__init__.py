from demo import db
from demo.models.fact import Fact


def create_all_db():
    db.create_all()
