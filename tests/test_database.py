import pytest


class TestInitDB:
    def test_init_creates_tables(self, _test_db):
        from models.database import daftar_langganan, authenticate

        user = authenticate("nonexistent", "x")
        assert user is None


class TestRegister:
    def test_register_success(self, _test_db):
        ok, msg = _test_db.register_user("newuser", "pass1234", "New User")
        assert ok
        assert "berhasil" in msg.lower()

    def test_register_empty_fields(self, _test_db):
        ok, msg = _test_db.register_user("", "pass", "Name")
        assert not ok

    def test_register_duplicate(self, _test_db):
        _test_db.register_user("user", "pass", "Name")
        ok, msg = _test_db.register_user("user", "pass2", "Name2")
        assert not ok
        assert "sudah digunakan" in msg.lower()


class TestAuthenticate:
    def test_login_success(self, _test_db):
        _test_db.register_user("loginuser", "mypass", "Login User")
        user = _test_db.authenticate("loginuser", "mypass")
        assert user is not None
        assert user["username"] == "loginuser"

    def test_login_wrong_password(self, _test_db):
        _test_db.register_user("user2", "pass", "User 2")
        user = _test_db.authenticate("user2", "wrong")
        assert user is None

    def test_login_nonexistent(self, _test_db):
        user = _test_db.authenticate("nobody", "pass")
        assert user is None


class TestSubscription:
    def _create_user(self, _test_db):
        _test_db.register_user("subuser", "pass", "Sub User")
        return _test_db.authenticate("subuser", "pass")["id"]

    def test_add_subscription(self, _test_db):
        uid = self._create_user(_test_db)
        from models.database import Subscription, tambah_langganan, daftar_langganan

        sid = tambah_langganan(Subscription(
            id=None, user_id=uid, nama="Netflix", kategori="Hiburan",
            harga=150000, siklus="Bulanan", tanggal_mulai="2026-01-01",
            tanggal_jatuh_tempo="2026-02-01", metode_pembayaran="Kartu Kredit",
            catatan="Family plan", status="Aktif",
        ))
        assert sid > 0
        rows = daftar_langganan(uid)
        assert len(rows) == 1
        assert rows[0]["nama"] == "Netflix"

    def test_delete_subscription(self, _test_db):
        uid = self._create_user(_test_db)
        from models.database import Subscription, tambah_langganan, hapus_langganan, daftar_langganan

        sid = tambah_langganan(Subscription(
            id=None, user_id=uid, nama="Spotify", kategori="Hiburan",
            harga=50000, siklus="Bulanan", tanggal_mulai="2026-01-01",
            tanggal_jatuh_tempo="2026-02-01", metode_pembayaran="", catatan="", status="Aktif",
        ))
        hapus_langganan(sid, uid)
        assert len(daftar_langganan(uid)) == 0

    def test_total_monthly(self, _test_db):
        uid = self._create_user(_test_db)
        from models.database import Subscription, tambah_langganan, total_bulan_ini

        tambah_langganan(Subscription(
            id=None, user_id=uid, nama="A", kategori="Hiburan",
            harga=100000, siklus="Bulanan", tanggal_mulai="2026-01-01",
            tanggal_jatuh_tempo="2026-02-01", metode_pembayaran="", catatan="", status="Aktif",
        ))
        tambah_langganan(Subscription(
            id=None, user_id=uid, nama="B", kategori="Produktivitas",
            harga=120000, siklus="Tahunan", tanggal_mulai="2026-01-01",
            tanggal_jatuh_tempo="2026-02-01", metode_pembayaran="", catatan="", status="Aktif",
        ))
        total = total_bulan_ini(uid)
        # 100000 (bulanan) + 120000/12 (tahunan) = 110000
        assert total == pytest.approx(110000, rel=0.1)
