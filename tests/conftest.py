import os
import sys
import tempfile

import pytest

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)


@pytest.fixture(autouse=True)
def _test_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    import config as cfg
    cfg.DB_PATH = db_path
    from models import database as db
    db.init_db()
    yield db
    os.unlink(db_path)


@pytest.fixture
def registered_user(_test_db):
    from controllers.auth_controller import AuthController
    ctrl = AuthController()
    ok, msg = ctrl.register("testuser", "test1234", "Test User")
    assert ok, msg
    return ctrl.login("testuser", "test1234")[0]


@pytest.fixture
def auth_ctrl(_test_db):
    from controllers.auth_controller import AuthController
    return AuthController()


@pytest.fixture
def sub_ctrl(_test_db, registered_user):
    from controllers.subscription_controller import SubscriptionController
    return SubscriptionController(), registered_user["id"]
