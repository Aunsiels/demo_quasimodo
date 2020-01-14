import os

import pytest

from quasimodo_website import Config, create_app

DB_TEST_PATH = 'sqlite:///' + os.path.abspath(os.path.dirname(__file__)) +\
               "/app_test.db"


@pytest.fixture
def app():
    Config.SQLALCHEMY_DATABASE_URI = DB_TEST_PATH
    Config.FACTS_PER_PAGE = 6
    app = create_app(True)
    return app