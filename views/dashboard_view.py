import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime

from views.sidebar_view import Sidebar
from views.toast import Toast
from controllers.subscription_controller import ValidationError
from controllers.budget_controller import BudgetController
import config


class DashboardFrame(tk.Frame):
    def __init__(self, parent, app, sub_controller):
        super().__init__(parent, bg=config.BG)
        self.app = app
        self.sub_ctrl = sub_controller
        self.user_id = app.current_user["id"]
        self.budget_ctrl = BudgetController()
        self._sort_col = None
        self._sort_rev = False

        Sidebar(self, app, active="Dashboard").pack(side=tk.LEFT, fill=tk.Y)
        content = tk.Frame(self, bg=config.BG)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            content, text=f"{config.ICON_HOUSE}  Dashboard",
            font=(config.FONT_FAMILY, 18, "bold"), bg=config.BG, fg=config.DARK,
        ).pack(anchor="w")

        filter_row = tk.Frame(content, bg=config.BG)
        filter_row.pack(fill=tk.X, pady=(12, 10))

        search_lbl = tk.Label(filter_row, text=f"{config.ICON_SEARCH}", font=("Segoe UI", 11),
                              bg=config.BG, fg=config.MUTED)
        search_lbl.pack(side=tk.LEFT, padx=(0, 4))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._refresh_tabel())
        self.search_entry = ttk.Entry(
            filter_row, textvariable=self.search_var, width=22,
            font=(config.FONT_FAMILY, 10),
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, 12), ipady=2)

        tk.Label(filter_row, text=f"{config.ICON_FILTER}  Kategori:", bg=config.BG,
                 fg=config.MUTED, font=(config.FONT_FAMILY, 9)).pack(side=tk.LEFT)
        self.kategori_var = tk.StringVar(value="")
        self.kategori_combo = ttk.Combobox(
            filter_row, textvariable=self.kategori_var,
            values=[""] + config.KATEGORI_LIST, state="readonly", width=16,
            font=(config.FONT_FAMILY, 10),
        )
        self.kategori_combo.pack(side=tk.LEFT, padx=(4, 12), ipady=1)
        self.kategori_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_tabel())

        tk.Label(filter_row, text="Status:", bg=config.BG, fg=config.MUTED,
                 font=(config.FONT_FAMILY, 9)).pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="")
        self.status_combo = ttk.Combobox(
            filter_row, textvariable=self.status_var,
            values=["", "Aktif", "Nonaktif"], state="readonly", width=12,
            font=(config.FONT_FAMILY, 10),
        )
        self.status_combo.pack(side=tk.LEFT, padx=(4, 0), ipady=1)
        self.status_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_tabel())

        summary = tk.Frame(content, bg=config.BG)
        summary.pack(fill=tk.X, pady=(0, 14))

        total = self.sub_ctrl.get_total_monthly(self.user_id)
        aktif = self.sub_ctrl.get_active(self.user_id)
        akan = self.sub_ctrl.get_upcoming(self.user_id, 7)

        total_fmt = f"Rp {total:,.0f}".replace(",", ".")
        self._kartu(summary, f"{config.ICON_MONEY}  Total Bulan Ini", total_fmt, config.ACCENT).pack(
            side=tk.LEFT, padx=(0, 14))
        self._kartu(summary, f"{config.ICON_LIST}  Langganan Aktif", str(len(aktif)), config.OK).pack(
            side=tk.LEFT, padx=(0, 14))
        self._kartu(summary, f"{config.ICON_CLOCK}  Jatuh Tempo (< 7 hari)", str(len(akan)), config.DANGER).pack(
            side=tk.LEFT)

        budget_status = self.budget_ctrl.get_budget_status(self.user_id)
        if budget_status:
            tk.Label(
                content, text=f"{config.ICON_BUDGET}  Status Budget Bulan Ini",
                font=(config.FONT_FAMILY, 12, "bold"), bg=config.BG, fg=config.DARK,
            ).pack(anchor="w", pady=(0, 6))

            bgt_frame = tk.Frame(content, bg=config.CARD_BG,
                                 highlightbackground=config.CARD_BORDER, highlightthickness=1)
            bgt_frame.pack(fill=tk.X, pady=(0, 16))

            for item in budget_status:
                self._budget_bar(bgt_frame, item)

        tk.Label(
            content, text=f"{config.ICON_BELL}  Segera Jatuh Tempo",
            font=(config.FONT_FAMILY, 12, "bold"), bg=config.BG, fg=config.DARK,
        ).pack(anchor="w", pady=(0, 6))

        up_frame = tk.Frame(content, bg=config.CARD_BG,
                            highlightbackground=config.CARD_BORDER, highlightthickness=1)
        up_frame.pack(fill=tk.X, pady=(0, 16))
        if akan:
            for sub in akan:
                self._baris_langganan(up_frame, sub)
        else:
            tk.Label(
                up_frame, text="Tidak ada langganan yang jatuh tempo dalam 7 hari ke depan.",
                bg=config.CARD_BG, fg=config.MUTED, font=(config.FONT_FAMILY, 9), pady=16,
            ).pack()

        header_row = tk.Frame(content, bg=config.BG)
        header_row.pack(fill=tk.X)
        tk.Label(
            header_row, text=f"{config.ICON_LIST}  Semua Langganan",
            font=(config.FONT_FAMILY, 12, "bold"), bg=config.BG, fg=config.DARK,
        ).pack(side=tk.LEFT)

        tbl_frame = tk.Frame(content, bg=config.CARD_BG,
                             highlightbackground=config.CARD_BORDER, highlightthickness=1)
        tbl_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Dash2.Treeview", background=config.CARD_BG, fieldbackground=config.CARD_BG,
            foreground=config.DARK, font=(config.FONT_FAMILY, 9), rowheight=34,
            borderwidth=0,
        )
        style.configure(
            "Dash2.Treeview.Heading", background="#F1F3F5", foreground=config.DARK,
            font=(config.FONT_FAMILY, 9, "bold"), borderwidth=0,
        )
        style.map(
            "Dash2.Treeview",
            background=[("selected", config.ACCENT_LIGHT)],
            foreground=[("selected", config.DARK)],
        )

        columns = ("nama", "kategori", "harga", "siklus", "jatuh_tempo", "status")
        self.tree = ttk.Treeview(
            tbl_frame, columns=columns, show="headings", height=8,
            style="Dash2.Treeview",
        )
        headers = {"nama": "Nama", "kategori": "Kategori", "harga": "Harga",
                   "siklus": "Siklus", "jatuh_tempo": "Jatuh Tempo", "status": "Status"}
        col_widths = {"nama": 170, "kategori": 120, "harga": 120,
                      "siklus": 100, "jatuh_tempo": 120, "status": 110}
        for col in columns:
            self.tree.heading(col, text=headers[col],
                              command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=col_widths[col], anchor="w")
        self.tree.tag_configure("odd", background=config.TABLE_ALT_ROW)
        self.tree.tag_configure("nonaktif", foreground=config.MUTED)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)

        self._refresh_tabel()

        self.tree.bind("<Double-1>", lambda e: self._edit_selected())

        content.bind("<Control-f>", lambda e: self._focus_search())
        content.bind("<Control-F>", lambda e: self._focus_search())
        content.bind("<Delete>", lambda e: self._hapus_selected())

        action_row = tk.Frame(content, bg=config.BG)
        action_row.pack(fill=tk.X, pady=(10, 0))

        self._tombol(action_row, f"  {config.ICON_PLUS}  Tambah Langganan", config.ACCENT,
                     config.ACCENT_HOVER, self.app.show_form).pack(side=tk.LEFT)
        self._tombol(action_row, f"  {config.ICON_ARCHIVE}  Aktif/Nonaktifkan", config.WARNING,
                     config.WARNING, lambda: self._toggle_selected()).pack(side=tk.LEFT, padx=(8, 0))
        self._tombol(action_row, f"  {config.ICON_CLOSE}  Hapus", config.DANGER,
                     config.DANGER_HOVER, lambda: self._hapus_selected()).pack(side=tk.LEFT, padx=(8, 0))
        self._tombol(action_row, f"  {config.ICON_SAVE}  Export CSV", config.OK,
                     config.OK_HOVER, lambda: self._export_csv()).pack(side=tk.LEFT, padx=(8, 0))
        tk.Label(
            action_row, text="* Klik dua kali baris untuk mengubah",
            bg=config.BG, fg=config.MUTED, font=(config.FONT_FAMILY, 8, "italic"),
        ).pack(side=tk.RIGHT)

    def _budget_bar(self, parent, item):
        row = tk.Frame(parent, bg=config.CARD_BG)
        row.pack(fill=tk.X, padx=16, pady=(8, 8))

        budget_fmt = f"Rp {item['budget']:,.0f}".replace(",", ".")
        spent_fmt = f"Rp {item['spent']:,.0f}".replace(",", ".")

        tk.Label(
            row, text=item["kategori"], font=(config.FONT_FAMILY, 9, "bold"),
            bg=config.CARD_BG, fg=config.DARK, width=14, anchor="w",
        ).pack(side=tk.LEFT)

        bar_bg = tk.Frame(row, bg=config.TABLE_ALT_ROW, height=12, width=160)
        bar_bg.pack(side=tk.LEFT, padx=(0, 10))
        bar_bg.pack_propagate(False)

        color = config.DANGER if item["over"] else config.ACCENT
        fill_w = max(int(160 * item["pct"] / 100), 4)
        tk.Frame(bar_bg, bg=color, width=fill_w, height=12).pack(side=tk.LEFT)

        tk.Label(
            row, text=f"{spent_fmt} / {budget_fmt}", font=(config.FONT_FAMILY, 8),
            bg=config.CARD_BG, fg=config.DARK,
        ).pack(side=tk.LEFT, padx=(0, 6))

        pct_label = tk.Label(
            row, text=f"{item['pct']:.0f}%", font=(config.FONT_FAMILY, 8, "bold"),
            bg=config.CARD_BG, fg=color,
        )
        pct_label.pack(side=tk.LEFT)

    def _focus_search(self):
        self.search_entry.focus_set()
        self.search_entry.selection_range(0, tk.END)

    def _kartu(self, parent, label, value, color):
        card = tk.Frame(
            parent, bg=config.CARD_BG, padx=18, pady=14,
            highlightbackground=config.CARD_BORDER, highlightthickness=1,
        )
        tk.Label(
            card, text=label, font=(config.FONT_FAMILY, 8), bg=config.CARD_BG, fg=config.MUTED,
        ).pack(anchor="w")
        tk.Label(
            card, text=value, font=(config.FONT_FAMILY, 18, "bold"),
            bg=config.CARD_BG, fg=color,
        ).pack(anchor="w", pady=(2, 0))
        return card

    def _baris_langganan(self, parent, sub):
        row = tk.Frame(parent, bg=config.CARD_BG)
        row.pack(fill=tk.X, padx=16, pady=(8, 8))
        due = datetime.date.fromisoformat(sub["tanggal_jatuh_tempo"])
        sisa_hari = (due - datetime.date.today()).days
        harga_fmt = f"Rp {sub['harga']:,.0f}".replace(",", ".")

        left = tk.Frame(row, bg=config.CARD_BG)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            left, text=sub["nama"], font=(config.FONT_FAMILY, 10, "bold"),
            bg=config.CARD_BG, fg=config.DARK,
        ).pack(anchor="w")
        tk.Label(
            left, text=sub["kategori"], font=(config.FONT_FAMILY, 8),
            bg=config.CARD_BG, fg=config.MUTED,
        ).pack(anchor="w")

        warna_sisa = config.DANGER if sisa_hari <= 2 else config.WARNING
        tk.Label(
            row, text=f"{sisa_hari} hari lagi", font=(config.FONT_FAMILY, 9),
            bg=config.CARD_BG, fg=warna_sisa,
        ).pack(side=tk.LEFT, padx=14)
        tk.Label(
            row, text=harga_fmt, font=(config.FONT_FAMILY, 9, "bold"),
            bg=config.CARD_BG, fg=config.DARK,
        ).pack(side=tk.RIGHT)

    def _tombol(self, parent, text, bg, hover, command):
        btn = tk.Button(
            parent, text=text, bg=bg, fg="white", relief=tk.FLAT,
            font=(config.FONT_FAMILY, 9, "bold"),
            command=command, cursor="hand2", padx=14, pady=6,
            activebackground=hover, activeforeground="white",
        )
        def on_enter(e): btn.config(bg=hover)
        def on_leave(e): btn.config(bg=bg)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _sort_by(self, col):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col
            self._sort_rev = False
        items = [(self.tree.set(iid, col), iid) for iid in self.tree.get_children("")]
        items.sort(key=lambda x: x[0].lower() if isinstance(x[0], str) else x[0],
                   reverse=self._sort_rev)
        for idx, (_, iid) in enumerate(items):
            self.tree.move(iid, "", idx)

    def _refresh_tabel(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        search = self.search_var.get().strip()
        kategori = self.kategori_var.get().strip()
        status = self.status_var.get().strip()

        semua = self.sub_ctrl.get_all_filtered(self.user_id, search, kategori, status)
        self._row_map = {}
        for i, sub in enumerate(semua):
            tag = "odd" if i % 2 else "even"
            if sub["status"] == "Nonaktif":
                tag = "nonaktif"
            harga_fmt = f"Rp {sub['harga']:,.0f}".replace(",", ".")
            status_display = f"{config.ICON_CHECK}  {sub['status']}" if sub["status"] == "Aktif" else sub["status"]
            iid = self.tree.insert(
                "", tk.END, tags=(tag,),
                values=(sub["nama"], sub["kategori"], harga_fmt,
                        sub["siklus"], sub["tanggal_jatuh_tempo"], status_display),
            )
            self._row_map[iid] = sub["id"]

    def _get_selected_sub_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Pilih salah satu baris terlebih dahulu.")
            return None
        return self._row_map[selected[0]]

    def _edit_selected(self):
        sub_id = self._get_selected_sub_id()
        if sub_id is None:
            return
        sub_row = self.sub_ctrl.get_by_id(sub_id, self.user_id)
        if sub_row:
            self.app.show_form(sub_row)

    def _toggle_selected(self):
        sub_id = self._get_selected_sub_id()
        if sub_id is None:
            return
        new_status = self.sub_ctrl.toggle_status(sub_id, self.user_id)
        Toast.show(self.app, f"Status diganti ke {new_status}", config.WARNING)
        self._refresh_tabel()

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
            title="Export Data Langganan",
        )
        if not path:
            return
        try:
            self.sub_ctrl.export_csv(self.user_id, path)
            messagebox.showinfo(f"{config.ICON_SAVE}  Berhasil",
                                f"Data berhasil diexport ke:\n{path}")
        except Exception as e:
            messagebox.showerror(f"{config.ICON_WARN}  Gagal", str(e))

    def _hapus_selected(self):
        sub_id = self._get_selected_sub_id()
        if sub_id is None:
            return
        if messagebox.askyesno("Konfirmasi", "Hapus langganan yang dipilih?"):
            self.sub_ctrl.delete(sub_id, self.user_id)
            Toast.show(self.app, "Langganan berhasil dihapus")
            self._refresh_tabel()
