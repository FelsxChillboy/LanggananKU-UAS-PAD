import sqlite3
import hashlib
import datetime
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional

import config

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    pass


@contextmanager
def _get_connection():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _hash_password(password: str, salt: str) -> str:
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    )
    return key.hex()


def init_db():
    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                display_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                kategori TEXT NOT NULL,
                amount REAL NOT NULL,
                UNIQUE(user_id, kategori),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                nama TEXT NOT NULL,
                kategori TEXT NOT NULL,
                harga REAL NOT NULL,
                siklus TEXT NOT NULL,
                tanggal_mulai TEXT NOT NULL,
                tanggal_jatuh_tempo TEXT NOT NULL,
                metode_pembayaran TEXT,
                catatan TEXT,
                status TEXT NOT NULL DEFAULT 'Aktif',
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        logger.info("Database initialized at %s", config.DB_PATH)


def register_user(username: str, password: str, display_name: str) -> tuple[bool, str]:
    if not username or not password or not display_name:
        return False, "Semua kolom wajib diisi."
    try:
        with _get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cur.fetchone():
                return False, "Username sudah digunakan, silakan pilih yang lain."
            salt = username.lower()
            pw_hash = _hash_password(password, salt)
            cur.execute(
                "INSERT INTO users (username, password_hash, display_name, created_at) VALUES (?, ?, ?, ?)",
                (username, pw_hash, display_name, datetime.datetime.now().isoformat()),
            )
            logger.info("User registered: %s", username)
            return True, "Akun berhasil dibuat. Silakan masuk."
    except sqlite3.Error as e:
        logger.exception("Database error during register_user for %s", username)
        return False, f"Terjadi kesalahan database: {e}"


def authenticate(username: str, password: str) -> Optional[sqlite3.Row]:
    try:
        with _get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cur.fetchone()
        if row is None:
            logger.warning("Login attempt for non-existent user: %s", username)
            return None
        salt = username.lower()
        pw_hash = _hash_password(password, salt)
        if pw_hash == row["password_hash"]:
            logger.info("User logged in: %s", username)
            return row
        # Fallback legacy SHA256
        old_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
        if old_hash == row["password_hash"]:
            logger.info("Upgrading password hash for user: %s", username)
            with _get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (pw_hash, row["id"]),
                )
            return row
        logger.warning("Failed login attempt for user: %s", username)
        return None
    except sqlite3.Error as e:
        logger.exception("Database error during authenticate for %s", username)
        raise DatabaseError(f"Gagal autentikasi: {e}") from e


@dataclass
class Subscription:
    id: Optional[int]
    user_id: int
    nama: str
    kategori: str
    harga: float
    siklus: str
    tanggal_mulai: str
    tanggal_jatuh_tempo: str
    metode_pembayaran: str
    catatan: str
    status: str = "Aktif"


def hitung_jatuh_tempo_berikutnya(tanggal_mulai: str, siklus: str) -> str:
    mulai = datetime.date.fromisoformat(tanggal_mulai)
    hari = config.SIKLUS_HARI.get(siklus, 30)
    today = datetime.date.today()
    due = mulai
    while due < today:
        due += datetime.timedelta(days=hari)
    return due.isoformat()


def tambah_langganan(sub: Subscription) -> int:
    try:
        with _get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO subscriptions
                (user_id, nama, kategori, harga, siklus, tanggal_mulai, tanggal_jatuh_tempo,
                 metode_pembayaran, catatan, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (sub.user_id, sub.nama, sub.kategori, sub.harga, sub.siklus, sub.tanggal_mulai,
                  sub.tanggal_jatuh_tempo, sub.metode_pembayaran, sub.catatan, sub.status))
            new_id = cur.lastrowid
            logger.debug("Subscription added: id=%d user=%d", new_id, sub.user_id)
            return new_id
    except sqlite3.Error as e:
        logger.exception("Failed to add subscription for user %d", sub.user_id)
        raise DatabaseError(f"Gagal menambah langganan: {e}") from e


def update_langganan(sub: Subscription):
    try:
        with _get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE subscriptions SET nama=?, kategori=?, harga=?, siklus=?, tanggal_mulai=?,
                tanggal_jatuh_tempo=?, metode_pembayaran=?, catatan=?, status=?
                WHERE id=? AND user_id=?
            """, (sub.nama, sub.kategori, sub.harga, sub.siklus, sub.tanggal_mulai,
                  sub.tanggal_jatuh_tempo, sub.metode_pembayaran, sub.catatan, sub.status,
                  sub.id, sub.user_id))
            logger.debug("Subscription updated: id=%d user=%d", sub.id, sub.user_id)
    except sqlite3.Error as e:
        logger.exception("Failed to update subscription %d", sub.id)
        raise DatabaseError(f"Gagal mengubah langganan: {e}") from e


def hapus_langganan(sub_id: int, user_id: int):
    try:
        with _get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM subscriptions WHERE id=? AND user_id=?", (sub_id, user_id))
            logger.debug("Subscription deleted: id=%d user=%d", sub_id, user_id)
    except sqlite3.Error as e:
        logger.exception("Failed to delete subscription %d", sub_id)
        raise DatabaseError(f"Gagal menghapus langganan: {e}") from e


def daftar_langganan(user_id: int, status: Optional[str] = None):
    try:
        with _get_connection() as conn:
            cur = conn.cursor()
            if status:
                cur.execute(
                    "SELECT * FROM subscriptions WHERE user_id=? AND status=? ORDER BY tanggal_jatuh_tempo ASC",
                    (user_id, status),
                )
            else:
                cur.execute(
                    "SELECT * FROM subscriptions WHERE user_id=? ORDER BY tanggal_jatuh_tempo ASC",
                    (user_id,),
                )
            return cur.fetchall()
    except sqlite3.Error as e:
        logger.exception("Failed to fetch subscriptions for user %d", user_id)
        raise DatabaseError(f"Gagal mengambil data langganan: {e}") from e


def daftar_langganan_filtered(user_id: int, search: str = "",
                              kategori: str = "", status: str = ""):
    query = "SELECT * FROM subscriptions WHERE user_id=?"
    params = [user_id]
    if search:
        query += " AND nama LIKE ?"
        params.append(f"%{search}%")
    if kategori:
        query += " AND kategori=?"
        params.append(kategori)
    if status:
        query += " AND status=?"
        params.append(status)
    query += " ORDER BY tanggal_jatuh_tempo ASC"
    try:
        with _get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.fetchall()
    except sqlite3.Error as e:
        logger.exception("Failed to fetch filtered subscriptions for user %d", user_id)
        raise DatabaseError(f"Gagal mengambil data langganan: {e}") from e


def toggle_status_langganan(sub_id: int, user_id: int) -> str:
    try:
        with _get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT status FROM subscriptions WHERE id=? AND user_id=?",
                        (sub_id, user_id))
            row = cur.fetchone()
            if not row:
                raise DatabaseError("Langganan tidak ditemukan.")
            new_status = "Nonaktif" if row["status"] == "Aktif" else "Aktif"
            cur.execute("UPDATE subscriptions SET status=? WHERE id=? AND user_id=?",
                        (new_status, sub_id, user_id))
            logger.debug("Subscription %d toggled to %s for user %d", sub_id, new_status, user_id)
            return new_status
    except sqlite3.Error as e:
        logger.exception("Failed to toggle status for subscription %d", sub_id)
        raise DatabaseError(f"Gagal mengubah status langganan: {e}") from e


def langganan_akan_jatuh_tempo(user_id: int, dalam_hari: int = 7):
    today = datetime.date.today()
    batas = today + datetime.timedelta(days=dalam_hari)
    rows = daftar_langganan(user_id, status="Aktif")
    hasil = []
    for r in rows:
        due = datetime.date.fromisoformat(r["tanggal_jatuh_tempo"])
        if today <= due <= batas:
            hasil.append(r)
    return hasil


def total_bulan_ini(user_id: int) -> float:
    rows = daftar_langganan(user_id, status="Aktif")
    total = 0.0
    for r in rows:
        if r["siklus"] == "Bulanan":
            total += r["harga"]
        elif r["siklus"] == "Mingguan":
            total += r["harga"] * 4.345
        elif r["siklus"] == "Tahunan":
            total += r["harga"] / 12
    return total


def pengeluaran_per_bulan(user_id: int) -> dict:
    rows = daftar_langganan(user_id, status="Aktif")
    per_kategori = {}
    for r in rows:
        bulanan = r["harga"]
        if r["siklus"] == "Mingguan":
            bulanan = r["harga"] * 4.345
        elif r["siklus"] == "Tahunan":
            bulanan = r["harga"] / 12
        per_kategori[r["kategori"]] = per_kategori.get(r["kategori"], 0) + bulanan
    return per_kategori


def set_budget(user_id: int, kategori: str, amount: float):
    try:
        with _get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO budgets (user_id, kategori, amount)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, kategori) DO UPDATE SET amount=excluded.amount
            """, (user_id, kategori, amount))
            logger.debug("Budget set for user %d, kategori %s: %.0f", user_id, kategori, amount)
    except sqlite3.Error as e:
        logger.exception("Failed to set budget for user %d", user_id)
        raise DatabaseError(f"Gagal menyimpan budget: {e}") from e


def get_budgets(user_id: int) -> dict:
    try:
        with _get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT kategori, amount FROM budgets WHERE user_id=?", (user_id,))
            return {row["kategori"]: row["amount"] for row in cur.fetchall()}
    except sqlite3.Error as e:
        logger.exception("Failed to get budgets for user %d", user_id)
        raise DatabaseError(f"Gagal mengambil budget: {e}") from e


def delete_budget(user_id: int, kategori: str):
    try:
        with _get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM budgets WHERE user_id=? AND kategori=?", (user_id, kategori))
    except sqlite3.Error as e:
        logger.exception("Failed to delete budget for user %d", user_id)
        raise DatabaseError(f"Gagal menghapus budget: {e}") from e


def update_user_display_name(user_id: int, display_name: str):
    try:
        with _get_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE users SET display_name=? WHERE id=?", (display_name, user_id))
    except sqlite3.Error as e:
        logger.exception("Failed to update display name for user %d", user_id)
        raise DatabaseError(f"Gagal mengupdate nama: {e}") from e


def update_user_password(user_id: int, new_password_hash: str):
    try:
        with _get_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE users SET password_hash=? WHERE id=?", (new_password_hash, user_id))
    except sqlite3.Error as e:
        logger.exception("Failed to update password for user %d", user_id)
        raise DatabaseError(f"Gagal mengupdate password: {e}") from e
