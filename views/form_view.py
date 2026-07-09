import tkinter as tk
from tkinter import ttk, messagebox
import datetime

from views.sidebar_view import Sidebar
from views.toast import Toast
from controllers.subscription_controller import ValidationError
import config


class SubscriptionFormFrame(tk.Frame):
    def __init__(self, parent, app, sub_controller, sub_row=None):
        super().__init__(parent, bg=config.BG)
        self.app = app
        self.sub_ctrl = sub_controller
        self.sub_row = sub_row
        self.editing = sub_row is not None

        Sidebar(self, app, active="Tambah Baru").pack(side=tk.LEFT, fill=tk.Y)
        content = tk.Frame(self, bg=config.BG)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        icon = config.ICON_GEAR if self.editing else config.ICON_PLUS
        judul = "Ubah Langganan" if self.editing else "Tambah Langganan Baru"
        tk.Label(
            content, text=f"{icon}  {judul}",
            font=(config.FONT_FAMILY, 18, "bold"), bg=config.BG, fg=config.DARK,
        ).pack(anchor="w", pady=(0, 18))

        card = tk.Frame(
            content, bg=config.CARD_BG, padx=28, pady=24,
            highlightbackground=config.CARD_BORDER, highlightthickness=1,
        )
        card.pack(fill=tk.X)

        self.vars = {}
        field_map = [
            ("Nama Layanan", "nama", "entry", 0, None),
            ("Kategori", "kategori", "combo", 0, config.KATEGORI_LIST),
            ("Harga (Rp)", "harga", "entry", 1, None),
            ("Siklus Tagihan", "siklus", "combo", 1, config.SIKLUS_LIST),
            ("Tanggal Mulai (YYYY-MM-DD)", "tanggal_mulai", "entry", 2, None),
            ("Metode Pembayaran", "metode_pembayaran", "entry", 2, None),
        ]
        hint_map = {
            "nama": "Contoh: Netflix, Spotify, dll.",
            "harga": "Gunakan angka saja, contoh: 150000",
            "tanggal_mulai": "Format: 2026-07-07",
            "metode_pembayaran": "Opsional: Kartu Kredit, Transfer, dll.",
        }

        for label, key, typ, row, options in field_map:
            col = 1 if key in ("kategori", "siklus", "metode_pembayaran") else 0
            actual_row = row if col == 0 else row

            tk.Label(
                card, text=label, font=(config.FONT_FAMILY, 9, "bold"),
                bg=config.CARD_BG, fg=config.DARK, anchor="w",
            ).grid(row=actual_row * 3, column=col, sticky="w",
                   padx=(0 if col == 0 else 24, 0), pady=(12, 2))

            if typ == "combo":
                var = tk.StringVar(value=options[0])
                combo = ttk.Combobox(
                    card, textvariable=var, values=options,
                    state="readonly", width=28, font=(config.FONT_FAMILY, 10),
                )
                combo.grid(row=actual_row * 3 + 1, column=col, sticky="we",
                           padx=(0 if col == 0 else 24, 0))
                self.vars[key] = var
            else:
                var = tk.StringVar()
                entry = ttk.Entry(
                    card, textvariable=var, width=30, font=(config.FONT_FAMILY, 10),
                )
                entry.grid(row=actual_row * 3 + 1, column=col, sticky="we",
                           padx=(0 if col == 0 else 24, 0), ipady=2)
                self.vars[key] = var

            hint = hint_map.get(key)
            if hint:
                tk.Label(
                    card, text=hint, font=(config.FONT_FAMILY, 8),
                    bg=config.CARD_BG, fg=config.MUTED, anchor="w",
                ).grid(row=actual_row * 3 + 2, column=col, sticky="w",
                       padx=(0 if col == 0 else 24, 0), pady=(1, 0))

        tk.Label(
            card, text="Catatan", font=(config.FONT_FAMILY, 9, "bold"),
            bg=config.CARD_BG, fg=config.DARK, anchor="w",
        ).grid(row=9, column=0, sticky="w", pady=(16, 2))
        self.catatan_text = tk.Text(card, height=3, width=68, font=(config.FONT_FAMILY, 9))
        self.catatan_text.grid(row=10, column=0, columnspan=2, sticky="we", pady=(0, 4))
        tk.Label(
            card, text="Opsional: catatan tambahan tentang langganan ini",
            font=(config.FONT_FAMILY, 8), bg=config.CARD_BG, fg=config.MUTED, anchor="w",
        ).grid(row=11, column=0, sticky="w")

        if self.editing:
            self._isi_form_dari_data(sub_row)
        else:
            self.vars["tanggal_mulai"].set(datetime.date.today().isoformat())

        btn_row = tk.Frame(content, bg=config.BG)
        btn_row.pack(fill=tk.X, pady=(18, 0))

        cancel_btn = tk.Button(
            btn_row, text=f"  {config.ICON_CLOSE}  BATAL", bg="#E6E7EB", fg=config.DARK,
            relief=tk.FLAT, font=(config.FONT_FAMILY, 9, "bold"),
            command=self.app.show_dashboard, padx=18, pady=7, cursor="hand2",
            activebackground="#D0D3D9", activeforeground=config.DARK,
        )
        content.bind("<Control-s>", lambda e: self._simpan())
        content.bind("<Control-S>", lambda e: self._simpan())

        cancel_btn.pack(side=tk.RIGHT, padx=(8, 0))
        self._add_hover(cancel_btn, "#E6E7EB", "#D0D3D9", config.DARK, config.DARK)

        self.simpan_btn = tk.Button(
            btn_row, text=f"  {config.ICON_SAVE}  SIMPAN", bg=config.ACCENT, fg="white",
            relief=tk.FLAT, font=(config.FONT_FAMILY, 9, "bold"),
            command=self._simpan, padx=18, pady=7, cursor="hand2",
            activebackground=config.ACCENT_HOVER, activeforeground="white",
        )
        self.simpan_btn.pack(side=tk.RIGHT)
        self._add_hover(self.simpan_btn, config.ACCENT, config.ACCENT_HOVER, "white", "white")

    def _add_hover(self, btn, normal, hover, fg_normal, fg_hover):
        def on_enter(e): btn.config(bg=hover, fg=fg_hover)
        def on_leave(e): btn.config(bg=normal, fg=fg_normal)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _isi_form_dari_data(self, sub_row):
        self.vars["nama"].set(sub_row["nama"])
        self.vars["kategori"].set(sub_row["kategori"])
        self.vars["harga"].set(str(sub_row["harga"]))
        self.vars["siklus"].set(sub_row["siklus"])
        self.vars["tanggal_mulai"].set(sub_row["tanggal_mulai"])
        self.vars["metode_pembayaran"].set(sub_row["metode_pembayaran"] or "")
        self.catatan_text.insert("1.0", sub_row["catatan"] or "")

    def _simpan(self):
        self.simpan_btn.config(state=tk.DISABLED, text=f"  {config.ICON_CLOCK}  Menyimpan...")
        self.update_idletasks()
        try:
            nama = self.vars["nama"].get().strip()
            kategori = self.vars["kategori"].get()
            harga_str = self.vars["harga"].get().strip()
            siklus = self.vars["siklus"].get()
            tanggal_mulai = self.vars["tanggal_mulai"].get().strip()
            metode = self.vars["metode_pembayaran"].get().strip()
            catatan = self.catatan_text.get("1.0", tk.END).strip()
            user_id = self.app.current_user["id"]

            if self.editing:
                self.sub_ctrl.update(
                    sub_id=self.sub_row["id"], user_id=user_id,
                    nama=nama, kategori=kategori, harga_str=harga_str, siklus=siklus,
                    tanggal_mulai=tanggal_mulai, metode=metode, catatan=catatan,
                    status=self.sub_row["status"],
                )
            else:
                self.sub_ctrl.add(
                    user_id=user_id, nama=nama, kategori=kategori, harga_str=harga_str,
                    siklus=siklus, tanggal_mulai=tanggal_mulai, metode=metode, catatan=catatan,
                )

            Toast.show(self.app, "Data langganan berhasil disimpan")
            self.app.show_dashboard()
        except ValidationError as e:
            messagebox.showerror(f"{config.ICON_WARN}  Validasi Gagal", str(e))
            self.simpan_btn.config(state=tk.NORMAL, text=f"  {config.ICON_SAVE}  SIMPAN")
