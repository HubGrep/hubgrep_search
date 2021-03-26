# fixes imports for pytest cases: https://stackoverflow.com/questions/49028611/pytest-cannot-find-module
# (cant find hubgrep module otherwise)
#
#
import os
import tempfile

import pytest

from flask_migrate import upgrade, init


from hubgrep import create_app
from hubgrep import db

@pytest.fixture(scope='class')
def test_app():
    app = create_app()
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
    yield app

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


@pytest.fixture(scope='class')
def test_client(test_app):
    yield test_app.test_client()
