import logging
from decimal import Decimal

from models import database as db
from models.database import DatabaseError
from controllers.subscription_controller import ValidationError

import config

logger = logging.getLogger(__name__)


class BudgetController:
    def get_budgets(self, user_id: int) -> dict:
        try:
            return db.get_budgets(user_id)
        except DatabaseError:
            logger.exception("Failed to get budgets for user %d", user_id)
            raise

    def set_budget(self, user_id: int, kategori: str, amount_str: str):
        if not kategori:
            raise ValidationError("Pilih kategori.")
        if not amount_str.strip():
            raise ValidationError("Jumlah budget wajib diisi.")
        try:
            amount = float(amount_str.replace(".", "").replace(",", "."))
            if amount <= 0:
                raise ValidationError("Budget harus lebih dari 0.")
        except ValueError:
            raise ValidationError("Budget harus berupa angka.")
        try:
            db.set_budget(user_id, kategori, amount)
            logger.info("Budget set: user=%d, kategori=%s, amount=%.0f", user_id, kategori, amount)
        except DatabaseError:
            logger.exception("Failed to set budget for user %d", user_id)
            raise

    def delete_budget(self, user_id: int, kategori: str):
        try:
            db.delete_budget(user_id, kategori)
        except DatabaseError:
            logger.exception("Failed to delete budget for user %d", user_id)
            raise

    def get_budget_status(self, user_id: int) -> list:
        budgets = self.get_budgets(user_id)
        spending = db.pengeluaran_per_bulan(user_id)
        result = []
        for kat in config.KATEGORI_LIST:
            budget = budgets.get(kat)
            spent = spending.get(kat, 0)
            if budget is not None and budget > 0:
                pct = min((spent / budget) * 100, 100)
                result.append({
                    "kategori": kat,
                    "budget": budget,
                    "spent": spent,
                    "pct": pct,
                    "over": spent > budget,
                })
        return result
