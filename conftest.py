# fixes imports for pytest cases: https://stackoverflow.com/questions/49028611/pytest-cannot-find-module
# (cant find hubgrep module otherwise)
#
#
import os
import tempfile
import logging

import pytest

from hubgrep import create_app
from hubgrep import db
from hubgrep.models import HostingService
logger = logging.getLogger(__name__)


def get_example_hoster():
    h = HostingService()
    h.api_url = 'https://example.com/api'
    h.config = '{}'
    h.landingpage_url = 'https://example.com'
    h.type = 'gitea'
    return h


@pytest.fixture(scope='class')
def test_app():
    app = create_app()
    db_fd, file_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{file_path}'

    with app.app_context():
        db.create_all()
        hoster = get_example_hoster()
        db.session.add(hoster)
        db.session.commit()
    yield app

    os.close(db_fd)
    os.unlink(file_path)


@pytest.fixture(scope='class')
def test_client(test_app):
    yield test_app.test_client()

