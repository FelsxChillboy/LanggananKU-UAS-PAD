import tkinter as tk
import config


class Sidebar(tk.Frame):
    MENUS = [
        (f"{config.ICON_HOUSE}  Dashboard", "Dashboard"),
        (f"{config.ICON_PLUS}  Tambah Baru", "Tambah Baru"),
        (f"{config.ICON_CHART}  Grafik & Insight", "Grafik & Insight"),
        (f"{config.ICON_BUDGET}  Budget", "Budget"),
        (f"{config.ICON_PROFILE}  Profil", "Profil"),
        (f"{config.ICON_DOOR}  Keluar", "Keluar"),
    ]

    def __init__(self, parent, app, active="Dashboard"):
        super().__init__(
            parent, bg=config.SIDEBAR_BG, width=200,
            highlightbackground=config.CARD_BORDER, highlightthickness=1,
        )
        self.app = app
        self.pack_propagate(False)

        header = tk.Frame(self, bg=config.SIDEBAR_BG, padx=16, pady=(20, 16))
        header.pack(fill=tk.X)
        user_name = app.current_user["display_name"] if app.current_user else ""
        tk.Label(
            header, text=f"{config.ICON_USER}  {user_name}",
            font=(config.FONT_FAMILY, 11, "bold"), bg=config.SIDEBAR_BG, fg=config.DARK,
            wraplength=170, justify="left",
        ).pack(anchor="w")

        sep = tk.Frame(self, bg=config.CARD_BORDER, height=1)
        sep.pack(fill=tk.X, padx=12)

        for label, menu_id in self.MENUS:
            is_active = (menu_id == active)
            self._menu_item(menu_id, label, is_active)

        sep2 = tk.Frame(self, bg=config.CARD_BORDER, height=1)
        sep2.pack(fill=tk.X, padx=12, pady=(6, 0))

        self._theme_toggle()

    def _menu_item(self, menu_id, label, is_active):
        btn_frame = tk.Frame(self, bg=config.SIDEBAR_BG)
        btn_frame.pack(fill=tk.X, padx=8, pady=(2, 0))

        indicator = tk.Frame(btn_frame, bg=config.ACCENT if is_active else config.SIDEBAR_BG, width=3)
        indicator.pack(side=tk.LEFT, fill=tk.Y)

        lbl = tk.Label(
            btn_frame, text=label,
            font=(config.FONT_FAMILY, 10, "bold" if is_active else "normal"),
            bg=config.SIDEBAR_ACTIVE_BG if is_active else config.SIDEBAR_BG,
            fg=config.ACCENT if is_active else config.DARK,
            anchor="w", padx=12, pady=10, cursor="hand2",
        )
        lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        btn_frame.pack_propagate(False)
        lbl.bind("<Button-1>", lambda e, m=menu_id: self._navigate(m))

        if not is_active:
            def on_enter(e, l=lbl, i=indicator):
                l.config(bg=config.SIDEBAR_HOVER_BG)
                i.config(bg=config.ACCENT_LIGHT)
            def on_leave(e, l=lbl, i=indicator):
                l.config(bg=config.SIDEBAR_BG)
                i.config(bg=config.SIDEBAR_BG)
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)

    def _theme_toggle(self):
        frame = tk.Frame(self, bg=config.SIDEBAR_BG)
        frame.pack(fill=tk.X, side=tk.BOTTOM, padx=12, pady=12)

        is_dark = config.current_theme == "dark"
        icon = "\U0001f31e" if is_dark else "\U0001f319"
        label = "Mode Terang" if is_dark else "Mode Gelap"

        btn = tk.Label(
            frame, text=f"{icon}  {label}",
            font=(config.FONT_FAMILY, 9), bg=config.TOGGLE_BG, fg=config.TOGGLE_FG,
            anchor="center", padx=12, pady=8, cursor="hand2",
        )
        btn.pack(fill=tk.X)
        btn.bind("<Button-1>", lambda e: self._toggle(btn))

    def _toggle(self, btn):
        self.app.toggle_theme()

    def _navigate(self, menu):
        if menu == "Dashboard":
            self.app.show_dashboard()
        elif menu == "Tambah Baru":
            self.app.show_form()
        elif menu == "Grafik & Insight":
            self.app.show_charts()
        elif menu == "Budget":
            self.app.show_budget()
        elif menu == "Profil":
            self.app.show_profile()
        elif menu == "Keluar":
            self.app.logout()
