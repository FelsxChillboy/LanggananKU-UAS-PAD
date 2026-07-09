import tkinter as tk
from tkinter import ttk, messagebox

from views.toast import Toast
from controllers.auth_controller import ValidationError
import config


class ProfileFrame(tk.Frame):
    def __init__(self, parent, app, auth_controller):
        super().__init__(parent, bg=config.BG)
        self.app = app
        self.auth = auth_controller
        self.user_id = app.current_user["id"]
        self.current_display = app.current_user["display_name"]

        from views.sidebar_view import Sidebar
        Sidebar(self, app, active="Profil").pack(side=tk.LEFT, fill=tk.Y)
        content = tk.Frame(self, bg=config.BG)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            content, text=f"{config.ICON_PROFILE}  Profil Pengguna",
            font=(config.FONT_FAMILY, 18, "bold"), bg=config.BG, fg=config.DARK,
        ).pack(anchor="w", pady=(0, 18))

        card = tk.Frame(
            content, bg=config.CARD_BG, padx=28, pady=24,
            highlightbackground=config.CARD_BORDER, highlightthickness=1,
        )
        card.pack(fill=tk.X)

        tk.Label(
            card, text=f"{config.ICON_USER}  Nama Lengkap",
            font=(config.FONT_FAMILY, 9, "bold"), bg=config.CARD_BG, fg=config.DARK,
        ).pack(anchor="w")
        self.name_var = tk.StringVar(value=self.current_display)
        self.name_entry = ttk.Entry(
            card, textvariable=self.name_var, width=32, font=(config.FONT_FAMILY, 10),
        )
        self.name_entry.pack(fill=tk.X, ipady=2, pady=(4, 16))

        tk.Label(
            card, text=f"{config.ICON_KEY}  Password Baru (kosongkan jika tidak diubah)",
            font=(config.FONT_FAMILY, 9, "bold"), bg=config.CARD_BG, fg=config.DARK,
        ).pack(anchor="w")
        self.pass_var = tk.StringVar()
        self.pass_entry = ttk.Entry(
            card, textvariable=self.pass_var, width=32, font=(config.FONT_FAMILY, 10),
            show="\u2022",
        )
        self.pass_entry.pack(fill=tk.X, ipady=2, pady=(4, 4))

        self.repass_var = tk.StringVar()
        self.repass_entry = ttk.Entry(
            card, textvariable=self.repass_var, width=32, font=(config.FONT_FAMILY, 10),
            show="\u2022",
        )
        self.repass_entry.pack(fill=tk.X, ipady=2, pady=(4, 18))

        btn_row = tk.Frame(card, bg=config.CARD_BG)
        btn_row.pack(fill=tk.X)

        tk.Button(
            btn_row, text=f"  {config.ICON_SAVE}  Simpan", bg=config.ACCENT, fg="white",
            font=(config.FONT_FAMILY, 9, "bold"), relief=tk.FLAT, padx=18, pady=7,
            cursor="hand2", activebackground=config.ACCENT_HOVER, activeforeground="white",
            command=self._save,
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_row, text=f"  {config.ICON_CLOSE}  Batal", bg="#E6E7EB", fg=config.DARK,
            font=(config.FONT_FAMILY, 9, "bold"), relief=tk.FLAT, padx=18, pady=7,
            cursor="hand2", command=self.app.show_dashboard,
        ).pack(side=tk.LEFT)

    def _save(self):
        name = self.name_var.get().strip()
        password = self.pass_var.get()
        repass = self.repass_var.get()

        if not name:
            messagebox.showerror(f"{config.ICON_WARN}  Validasi Gagal", "Nama lengkap wajib diisi.")
            return
        if password and password != repass:
            messagebox.showerror(f"{config.ICON_WARN}  Validasi Gagal", "Password baru tidak cocok.")
            return
        if password and len(password) < 4:
            messagebox.showerror(f"{config.ICON_WARN}  Validasi Gagal",
                                "Password minimal 4 karakter.")
            return

        try:
            self.auth.update_profile(self.user_id, name, password,
                                     username=self.app.current_user["username"])
            self.app.current_user["display_name"] = name
            Toast.show(self.app, "Profil berhasil diperbarui")
            self.app.show_dashboard()
        except ValidationError as e:
            messagebox.showerror(f"{config.ICON_WARN}  Error", str(e))
