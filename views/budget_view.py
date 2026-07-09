import tkinter as tk
from tkinter import ttk, messagebox

from views.toast import Toast
from controllers.subscription_controller import ValidationError
import config


class BudgetDialog(tk.Toplevel):
    def __init__(self, parent, app, budget_controller):
        super().__init__(parent)
        self.app = app
        self.budget_ctrl = budget_controller
        self.user_id = app.current_user["id"]

        self.title("Atur Budget per Kategori")
        self.configure(bg=config.CARD_BG)
        self.resizable(False, False)

        tk.Label(
            self, text=f"{config.ICON_BUDGET}  Budget per Kategori",
            font=(config.FONT_FAMILY, 14, "bold"), bg=config.CARD_BG, fg=config.DARK,
        ).pack(padx=24, pady=(20, 16))

        card = tk.Frame(self, bg=config.CARD_BG,
                        highlightbackground=config.CARD_BORDER, highlightthickness=1)
        card.pack(padx=24, pady=(0, 16), fill=tk.X)

        self.entries = {}
        existing = self.budget_ctrl.get_budgets(self.user_id)
        for i, kat in enumerate(config.KATEGORI_LIST):
            row = tk.Frame(card, bg=config.CARD_BG)
            row.pack(fill=tk.X, padx=16, pady=(8, 8))

            tk.Label(
                row, text=f"{kat}", font=(config.FONT_FAMILY, 10),
                bg=config.CARD_BG, fg=config.DARK, width=16, anchor="w",
            ).pack(side=tk.LEFT)

            var = tk.StringVar(value=f"{existing.get(kat, ''):.0f}" if existing.get(kat) else "")
            entry = ttk.Entry(row, textvariable=var, width=16, font=(config.FONT_FAMILY, 10))
            entry.pack(side=tk.LEFT, padx=(0, 8), ipady=2)
            self.entries[kat] = var

            tk.Label(
                row, text="Rp/bulan", font=(config.FONT_FAMILY, 8),
                bg=config.CARD_BG, fg=config.MUTED,
            ).pack(side=tk.LEFT)

        btn_row = tk.Frame(self, bg=config.CARD_BG)
        btn_row.pack(pady=(0, 20))

        tk.Button(
            btn_row, text=f"  {config.ICON_SAVE}  Simpan", bg=config.ACCENT, fg="white",
            font=(config.FONT_FAMILY, 9, "bold"), relief=tk.FLAT, padx=18, pady=6,
            cursor="hand2", activebackground=config.ACCENT_HOVER, activeforeground="white",
            command=self._save,
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_row, text=f"  {config.ICON_CLOSE}  Tutup", bg="#E6E7EB", fg=config.DARK,
            font=(config.FONT_FAMILY, 9, "bold"), relief=tk.FLAT, padx=18, pady=6,
            cursor="hand2", command=self.destroy,
        ).pack(side=tk.LEFT)

        self.update_idletasks()
        w = max(self.winfo_reqwidth(), 420)
        h = self.winfo_reqheight()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = parent.winfo_rootx() + (pw - w) // 2
        y = parent.winfo_rooty() + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.grab_set()

    def _save(self):
        for kat, var in self.entries.items():
            val = var.get().strip()
            if val:
                try:
                    self.budget_ctrl.set_budget(self.user_id, kat, val)
                except ValidationError as e:
                    messagebox.showerror(f"{config.ICON_WARN}  Error", f"{kat}: {e}")
                    return
            else:
                try:
                    self.budget_ctrl.delete_budget(self.user_id, kat)
                except Exception:
                    pass
        Toast.show(self.app, "Budget berhasil disimpan")
        self.destroy()
