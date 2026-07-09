import logging
from typing import Optional

from models import database as db
from models.database import DatabaseError

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    pass


class ValidationError(Exception):
    pass


class AuthController:
    def login(self, username: str, password: str) -> tuple[Optional[object], Optional[str]]:
        if not username.strip():
            return None, "Username tidak boleh kosong."
        if not password:
            return None, "Password tidak boleh kosong."
        try:
            user = db.authenticate(username.strip(), password)
            if user is None:
                return None, "Username atau password salah."
            return user, None
        except DatabaseError as e:
            logger.exception("Login failed for user: %s", username)
            return None, str(e)

    def register(self, username: str, password: str, display_name: str) -> tuple[bool, str]:
        username = username.strip()
        display_name = display_name.strip()
        if not username or not password or not display_name:
            return False, "Semua kolom wajib diisi."
        if len(username) < 3:
            return False, "Username minimal 3 karakter."
        if len(password) < 4:
            return False, "Password minimal 4 karakter."
        if len(display_name) < 1:
            return False, "Nama lengkap wajib diisi."
        try:
            return db.register_user(username, password, display_name)
        except DatabaseError as e:
            logger.exception("Registration failed for user: %s", username)
            return False, str(e)

    def update_profile(self, user_id: int, display_name: str, new_password: str = "",
                       username: str = ""):
        if not display_name.strip():
            raise ValidationError("Nama lengkap wajib diisi.")
        try:
            db.update_user_display_name(user_id, display_name.strip())
            if new_password:
                if len(new_password) < 4:
                    raise ValidationError("Password minimal 4 karakter.")
                salt = (username.lower() if username else f"user_{user_id}")
                key = db._hash_password(new_password, salt)
                db.update_user_password(user_id, key)
                logger.info("Password changed for user %d", user_id)
        except DatabaseError as e:
            logger.exception("Failed to update profile for user %d", user_id)
            raise ValidationError(str(e))
