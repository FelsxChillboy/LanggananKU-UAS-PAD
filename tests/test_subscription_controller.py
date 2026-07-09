import pytest


class TestSubscriptionController:
    def test_add_subscription(self, sub_ctrl):
        ctrl, uid = sub_ctrl
        sid = ctrl.add(
            user_id=uid, nama="Netflix", kategori="Hiburan",
            harga_str="150000", siklus="Bulanan",
            tanggal_mulai="2026-01-01", metode="Kartu Kredit", catatan="",
        )
        assert sid > 0

    def test_add_invalid_price(self, sub_ctrl):
        ctrl, uid = sub_ctrl
        from controllers.subscription_controller import ValidationError
        with pytest.raises(ValidationError):
            ctrl.add(
                user_id=uid, nama="Test", kategori="Hiburan",
                harga_str="abc", siklus="Bulanan",
                tanggal_mulai="2026-01-01", metode="", catatan="",
            )

    def test_add_empty_name(self, sub_ctrl):
        ctrl, uid = sub_ctrl
        from controllers.subscription_controller import ValidationError
        with pytest.raises(ValidationError):
            ctrl.add(
                user_id=uid, nama="", kategori="Hiburan",
                harga_str="50000", siklus="Bulanan",
                tanggal_mulai="2026-01-01", metode="", catatan="",
            )

    def test_list_subscriptions(self, sub_ctrl):
        ctrl, uid = sub_ctrl
        ctrl.add(uid, "A", "Hiburan", "100000", "Bulanan", "2026-01-01", "", "")
        ctrl.add(uid, "B", "Produktivitas", "50000", "Bulanan", "2026-01-01", "", "")
        all_subs = ctrl.get_all(uid)
        assert len(all_subs) == 2

    def test_delete_subscription(self, sub_ctrl):
        ctrl, uid = sub_ctrl
        sid = ctrl.add(uid, "Test", "Hiburan", "75000", "Bulanan", "2026-01-01", "", "")
        ctrl.delete(sid, uid)
        assert len(ctrl.get_all(uid)) == 0

    def test_get_total_monthly(self, sub_ctrl):
        ctrl, uid = sub_ctrl
        ctrl.add(uid, "A", "Hiburan", "100000", "Bulanan", "2026-01-01", "", "")
        ctrl.add(uid, "B", "Lainnya", "120000", "Tahunan", "2026-01-01", "", "")
        total = ctrl.get_total_monthly(uid)
        # 100000 + 120000/12 = 110000
        assert total == pytest.approx(110000, rel=0.1)
