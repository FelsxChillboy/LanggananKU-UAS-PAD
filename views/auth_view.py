import tkinter as tk
from tkinter import ttk, messagebox
import config


class LoginFrame(tk.Frame):
    def __init__(self, parent, app, auth_controller):
        super().__init__(parent, bg=config.BG)
        self.app = app
        self.auth = auth_controller

        container = tk.Frame(self, bg=config.BG)
        container.place(relx=0.5, rely=0.45, anchor="center")

        card = tk.Frame(
            container, bg=config.CARD_BG, padx=44, pady=36,
            highlightbackground=config.CARD_BORDER, highlightthickness=1,
        )
        card.pack()

        tk.Label(
            card, text=f"{config.ICON_WALLET}  LanggananKu",
            font=(config.FONT_FAMILY, 24, "bold"), fg=config.ACCENT, bg=config.CARD_BG,
        ).pack(pady=(0, 2))
        tk.Label(
            card, text="Pelacak Langganan Otomatis",
            font=(config.FONT_FAMILY, 10), fg=config.MUTED, bg=config.CARD_BG,
        ).pack(pady=(0, 28))

        for img, label, key, show in [
            (config.ICON_USER, "Username", "user", False),
            (config.ICON_LOCK, "Password", "pass", True),
        ]:
            frame = tk.Frame(card, bg=config.CARD_BG)
            frame.pack(fill=tk.X, pady=(0, 14))

            tk.Label(
                frame, text=f"{img}  {label}",
                font=(config.FONT_FAMILY, 9, "bold"), bg=config.CARD_BG, fg=config.DARK, anchor="w",
            ).pack(anchor="w", pady=(0, 4))

            entry = ttk.Entry(frame, width=32, font=(config.FONT_FAMILY, 10), show="\u2022" if show else "")
            entry.pack(fill=tk.X, ipady=2)
            if key == "user":
                self.username_entry = entry
            else:
                self.password_entry = entry
                entry.bind("<Return>", lambda e: self._login())

        self.login_btn = tk.Button(
            card, text=f"  {config.ICON_LOCK}  MASUK",
            bg=config.ACCENT, fg="white",
            font=(config.FONT_FAMILY, 10, "bold"),
            relief=tk.FLAT, activebackground=config.ACCENT_HOVER, activeforeground="white",
            command=self._login, width=30, pady=8, cursor="hand2",
        )
        self.login_btn.pack(pady=(6, 14))
        self._add_hover(self.login_btn, config.ACCENT, config.ACCENT_HOVER)

        register_link = tk.Label(
            card, text="Belum punya akun? Daftar di sini",
            fg=config.ACCENT, bg=config.CARD_BG,
            font=(config.FONT_FAMILY, 9), cursor="hand2",
        )
        register_link.pack()
        register_link.bind("<Button-1>", lambda e: self.app.show_register())

    def _add_hover(self, btn, normal, hover):
        def on_enter(e): btn.config(bg=hover)
        def on_leave(e): btn.config(bg=normal)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _login(self):
        self.login_btn.config(state=tk.DISABLED, text=f"  {config.ICON_CLOCK}  Memproses...")
        self.update_idletasks()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        user, error = self.auth.login(username, password)
        if error:
            messagebox.showerror(f"{config.ICON_WARN}  Gagal Masuk", error)
            self.login_btn.config(state=tk.NORMAL, text=f"  {config.ICON_LOCK}  MASUK")
            return
        self.app.login_success(user)


class RegisterFrame(tk.Frame):
    def __init__(self, parent, app, auth_controller):
        super().__init__(parent, bg=config.BG)
        self.app = app
        self.auth = auth_controller

        container = tk.Frame(self, bg=config.BG)
        container.place(relx=0.5, rely=0.45, anchor="center")

        card = tk.Frame(
            container, bg=config.CARD_BG, padx=44, pady=36,
            highlightbackground=config.CARD_BORDER, highlightthickness=1,
        )
        card.pack()

        tk.Label(
            card, text="Buat Akun Baru",
            font=(config.FONT_FAMILY, 20, "bold"), fg=config.DARK, bg=config.CARD_BG,
        ).pack(pady=(0, 4))
        tk.Label(
            card, text="Multi-user: tiap anggota punya data langganan sendiri",
            font=(config.FONT_FAMILY, 9), fg=config.MUTED, bg=config.CARD_BG,
        ).pack(pady=(0, 24))

        self.entries = {}
        fields = [
            (config.ICON_USER, "Nama Lengkap", "name"),
            (config.ICON_MAIL, "Username", "user"),
            (config.ICON_LOCK, "Password", "pass"),
        ]
        for img, label, key in fields:
            frame = tk.Frame(card, bg=config.CARD_BG)
            frame.pack(fill=tk.X, pady=(0, 14))

            tk.Label(
                frame, text=f"{img}  {label}",
                font=(config.FONT_FAMILY, 9, "bold"), bg=config.CARD_BG, fg=config.DARK, anchor="w",
            ).pack(anchor="w", pady=(0, 4))

            show = "\u2022" if key == "pass" else ""
            entry = ttk.Entry(frame, width=32, font=(config.FONT_FAMILY, 10), show=show)
            entry.pack(fill=tk.X, ipady=2)
            self.entries[key] = entry

        self.register_btn = tk.Button(
            card, text=f"  {config.ICON_CHECK}  DAFTAR",
            bg=config.OK, fg="white",
            font=(config.FONT_FAMILY, 10, "bold"),
            relief=tk.FLAT, activebackground=config.OK_HOVER, activeforeground="white",
            command=self._register, width=30, pady=8, cursor="hand2",
        )
        self.register_btn.pack(pady=(6, 14))
        self._add_hover(self.register_btn, config.OK, config.OK_HOVER)

        back_link = tk.Label(
            card, text=f"\u2190  Kembali ke halaman masuk",
            fg=config.ACCENT, bg=config.CARD_BG,
            font=(config.FONT_FAMILY, 9), cursor="hand2",
        )
        back_link.pack()
        back_link.bind("<Button-1>", lambda e: self.app.show_login())

    def _add_hover(self, btn, normal, hover):
        def on_enter(e): btn.config(bg=hover)
        def on_leave(e): btn.config(bg=normal)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _register(self):
        self.register_btn.config(state=tk.DISABLED, text=f"  {config.ICON_CLOCK}  Memproses...")
        self.update_idletasks()
        name = self.entries["name"].get().strip()
        username = self.entries["user"].get().strip()
        password = self.entries["pass"].get()
        ok, msg = self.auth.register(username, password, name)
        if ok:
            messagebox.showinfo(f"{config.ICON_CHECK}  Berhasil", msg)
            self.app.show_login()
        else:
            messagebox.showerror(f"{config.ICON_WARN}  Gagal Daftar", msg)
            self.register_btn.config(state=tk.NORMAL, text=f"  {config.ICON_CHECK}  DAFTAR")
