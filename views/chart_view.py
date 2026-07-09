import tkinter as tk

from views.sidebar_view import Sidebar
import charts
import config


class ChartFrame(tk.Frame):
    def __init__(self, parent, app, sub_controller):
        super().__init__(parent, bg=config.BG)
        self.app = app
        self.sub_ctrl = sub_controller
        user_id = app.current_user["id"]

        Sidebar(self, app, active="Grafik & Insight").pack(side=tk.LEFT, fill=tk.Y)
        content = tk.Frame(self, bg=config.BG)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            content, text=f"{config.ICON_CHART}  Grafik & Insight Pengeluaran",
            font=(config.FONT_FAMILY, 18, "bold"), bg=config.BG, fg=config.DARK,
        ).pack(anchor="w", pady=(0, 14))

        chart_card = tk.Frame(
            content, bg=config.CARD_BG,
            highlightbackground=config.CARD_BORDER, highlightthickness=1,
        )
        chart_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        per_kategori = self.sub_ctrl.get_monthly_by_category(user_id)
        jumlah_aktif = len(self.sub_ctrl.get_active(user_id))

        chart_frame = charts.buat_frame_grafik(chart_card, per_kategori, jumlah_aktif)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
