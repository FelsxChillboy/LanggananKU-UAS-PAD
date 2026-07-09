import csv
import datetime
import logging
import os
from typing import Optional

from models import database as db
from models.database import DatabaseError

import config

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    pass


class SubscriptionController:
    def get_all(self, user_id: int):
        try:
            return db.daftar_langganan(user_id)
        except DatabaseError as e:
            logger.exception("Failed to get subscriptions for user %d", user_id)
            raise

    def get_active(self, user_id: int):
        try:
            return db.daftar_langganan(user_id, status="Aktif")
        except DatabaseError as e:
            logger.exception("Failed to get active subscriptions for user %d", user_id)
            raise

    def get_by_id(self, sub_id: int, user_id: int):
        try:
            rows = db.daftar_langganan(user_id)
            for r in rows:
                if r["id"] == sub_id:
                    return r
            return None
        except DatabaseError as e:
            logger.exception("Failed to get subscription %d for user %d", sub_id, user_id)
            raise

    def get_upcoming(self, user_id: int, days: int = 7):
        try:
            return db.langganan_akan_jatuh_tempo(user_id, days)
        except DatabaseError as e:
            logger.exception("Failed to get upcoming subscriptions for user %d", user_id)
            raise

    def get_total_monthly(self, user_id: int) -> float:
        try:
            return db.total_bulan_ini(user_id)
        except DatabaseError as e:
            logger.exception("Failed to get total monthly for user %d", user_id)
            raise

    def get_monthly_by_category(self, user_id: int) -> dict:
        try:
            return db.pengeluaran_per_bulan(user_id)
        except DatabaseError as e:
            logger.exception("Failed to get monthly by category for user %d", user_id)
            raise

    def _validate(self, nama: str, harga_str: str, tanggal_mulai: str, editing: bool = False):
        errors = []
        if not nama.strip():
            errors.append("Nama layanan wajib diisi.")
        if not harga_str:
            errors.append("Harga wajib diisi.")
        else:
            try:
                harga = float(harga_str.replace(".", "").replace(",", "."))
                if harga <= 0:
                    errors.append("Harga harus lebih dari 0.")
            except ValueError:
                errors.append("Harga harus berupa angka.")
        if not tanggal_mulai.strip():
            errors.append("Tanggal mulai wajib diisi.")
        else:
            try:
                datetime.date.fromisoformat(tanggal_mulai.strip())
            except ValueError:
                errors.append("Tanggal mulai harus berformat YYYY-MM-DD, contoh: 2026-07-07.")
        return errors

    def add(self, user_id: int, nama: str, kategori: str, harga_str: str,
            siklus: str, tanggal_mulai: str, metode: str, catatan: str) -> int:
        errors = self._validate(nama, harga_str, tanggal_mulai)
        if errors:
            raise ValidationError("\n".join(errors))
        harga = float(harga_str.replace(".", "").replace(",", "."))
        try:
            return db.tambah_langganan(db.Subscription(
                id=None, user_id=user_id, nama=nama.strip(), kategori=kategori,
                harga=harga, siklus=siklus, tanggal_mulai=tanggal_mulai.strip(),
                tanggal_jatuh_tempo=db.hitung_jatuh_tempo_berikutnya(tanggal_mulai.strip(), siklus),
                metode_pembayaran=metode.strip(), catatan=catatan.strip(), status="Aktif",
            ))
        except DatabaseError as e:
            logger.exception("Failed to add subscription for user %d", user_id)
            raise

    def update(self, sub_id: int, user_id: int, nama: str, kategori: str,
               harga_str: str, siklus: str, tanggal_mulai: str, metode: str,
               catatan: str, status: str):
        errors = self._validate(nama, harga_str, tanggal_mulai, editing=True)
        if errors:
            raise ValidationError("\n".join(errors))
        harga = float(harga_str.replace(".", "").replace(",", "."))
        try:
            db.update_langganan(db.Subscription(
                id=sub_id, user_id=user_id, nama=nama.strip(), kategori=kategori,
                harga=harga, siklus=siklus, tanggal_mulai=tanggal_mulai.strip(),
                tanggal_jatuh_tempo=db.hitung_jatuh_tempo_berikutnya(tanggal_mulai.strip(), siklus),
                metode_pembayaran=metode.strip(), catatan=catatan.strip(), status=status,
            ))
        except DatabaseError as e:
            logger.exception("Failed to update subscription %d for user %d", sub_id, user_id)
            raise

    def get_all_filtered(self, user_id: int, search: str = "",
                         kategori: str = "", status: str = ""):
        try:
            return db.daftar_langganan_filtered(user_id, search, kategori, status)
        except DatabaseError:
            logger.exception("Failed to get filtered subscriptions for user %d", user_id)
            raise

    def toggle_status(self, sub_id: int, user_id: int) -> str:
        try:
            return db.toggle_status_langganan(sub_id, user_id)
        except DatabaseError:
            logger.exception("Failed to toggle status for subscription %d", sub_id)
            raise

    def export_csv(self, user_id: int, filepath: str):
        try:
            rows = db.daftar_langganan(user_id)
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Nama", "Kategori", "Harga", "Siklus",
                                 "Tanggal Mulai", "Jatuh Tempo", "Metode", "Catatan", "Status"])
                for r in rows:
                    writer.writerow([
                        r["nama"], r["kategori"], r["harga"], r["siklus"],
                        r["tanggal_mulai"], r["tanggal_jatuh_tempo"],
                        r["metode_pembayaran"], r["catatan"], r["status"],
                    ])
            logger.info("Exported %d subscriptions for user %d to %s", len(rows), user_id, filepath)
        except (DatabaseError, OSError) as e:
            logger.exception("Failed to export CSV for user %d", user_id)
            raise

    def delete(self, sub_id: int, user_id: int):
        try:
            db.hapus_langganan(sub_id, user_id)
        except DatabaseError as e:
            logger.exception("Failed to delete subscription %d for user %d", sub_id, user_id)
            raise
