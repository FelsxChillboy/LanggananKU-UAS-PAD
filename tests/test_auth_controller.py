import pytest


class TestAuthController:
    def test_register_success(self, auth_ctrl):
        ok, msg = auth_ctrl.register("newuser", "pass123", "New User")
        assert ok

    def test_register_short_password(self, auth_ctrl):
        ok, msg = auth_ctrl.register("user", "ab", "Name")
        assert not ok
        assert "minimal 4" in msg.lower()

    def test_register_short_username(self, auth_ctrl):
        ok, msg = auth_ctrl.register("ab", "pass123", "Name")
        assert not ok
        assert "minimal 3" in msg.lower()

    def test_login_ok(self, auth_ctrl):
        auth_ctrl.register("user", "pass", "User")
        user, err = auth_ctrl.login("user", "pass")
        assert user is not None
        assert err is None

    def test_login_wrong(self, auth_ctrl):
        auth_ctrl.register("user", "pass", "User")
        user, err = auth_ctrl.login("user", "wrong")
        assert user is None
        assert err is not None

    def test_login_empty(self, auth_ctrl):
        user, err = auth_ctrl.login("", "")
        assert user is None
        assert err is not None

    def test_duplicate_username(self, auth_ctrl):
        auth_ctrl.register("user", "pass", "User")
        ok, msg = auth_ctrl.register("user", "pass2", "User2")
        assert not ok
