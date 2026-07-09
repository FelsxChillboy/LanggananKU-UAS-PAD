import tkinter as tk
from tkinter import ttk
import logging

from models import database as db
from controllers.auth_controller import AuthController
from controllers.subscription_controller import SubscriptionController
from controllers.budget_controller import BudgetController
from views.auth_view import LoginFrame, RegisterFrame
from views.dashboard_view import DashboardFrame
from views.form_view import SubscriptionFormFrame
from views.chart_view import ChartFrame
from views.budget_view import BudgetDialog
from views.profile_view import ProfileFrame
from notifier import NotifierService
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class LangganankuApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(config.APP_TITLE)
        self.geometry(config.APP_GEOMETRY)
        self.minsize(config.APP_MIN_WIDTH, config.APP_MIN_HEIGHT)
        self.configure(bg=config.BG)

        config.load_theme()

        self.current_user = None
        self._current_view = None
        self._form_sub_row = None

        self.auth_ctrl = AuthController()
        self.sub_ctrl = SubscriptionController()
        self.budget_ctrl = BudgetController()

        self.container = tk.Frame(self, bg=config.BG)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.notifier = NotifierService(
            get_current_user_id_callback=lambda: self.current_user["id"] if self.current_user else None,
            on_open_window=self._restore_window,
        )
        self.notifier.start_background_checks()
        self.notifier.start_tray_icon()

        self._setup_styles()
        self._build_status_bar()

        self._bind_global_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        logger.info("Application started")
        self.show_login()

    def _bind_global_shortcuts(self):
        self.bind("<Control-n>", lambda e: self._shortcut_form())
        self.bind("<Control-N>", lambda e: self._shortcut_form())
        self.bind("<Escape>", lambda e: self._shortcut_escape())

    def _shortcut_form(self):
        if self.current_user and self._current_view not in ("login", "register"):
            self.show_form()

    def _shortcut_escape(self):
        if self._current_view in ("form", "chart", "profile"):
            self.show_dashboard()
        elif self._current_view == "register":
            self.show_login()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TEntry", fieldbackground=config.INPUT_BG, foreground=config.DARK,
                        font=(config.FONT_FAMILY, 10), borderwidth=0)
        style.configure("TCombobox", fieldbackground=config.CARD_BG, foreground=config.DARK,
                        font=(config.FONT_FAMILY, 10))
        style.configure("Vertical.TScrollbar", gripcount=0,
                        background=config.CARD_BORDER, troughcolor=config.BG,
                        arrowcolor=config.DARK)

    def _build_status_bar(self):
        self.status_bar = tk.Frame(self, bg=config.STATUSBAR_BG, height=28,
                                   highlightbackground=config.CARD_BORDER, highlightthickness=1)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        self.status_label = tk.Label(
            self.status_bar, text="", bg=config.STATUSBAR_BG, fg=config.MUTED,
            font=(config.FONT_FAMILY, 8), anchor="w", padx=14,
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _update_status(self):
        if self.current_user:
            user_id = self.current_user["id"]
            try:
                aktif = self.sub_ctrl.get_active(user_id)
                total = self.sub_ctrl.get_total_monthly(user_id)
                total_fmt = f"Rp {total:,.0f}".replace(",", ".")
                user_display = self.current_user["display_name"]
                self.status_label.config(
                    text=f"{config.ICON_USER}  {user_display}  |  "
                         f"{config.ICON_LIST}  {len(aktif)} langganan aktif  |  "
                         f"{config.ICON_MONEY}  {total_fmt}/bulan",
                )
            except Exception:
                self.status_label.config(
                    text=f"{config.ICON_USER}  {self.current_user['display_name']}",
                )
        else:
            self.status_label.config(text="")

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def _apply_bg(self):
        self.configure(bg=config.BG)
        self.container.configure(bg=config.BG)
        self.status_bar.configure(bg=config.STATUSBAR_BG,
                                  highlightbackground=config.CARD_BORDER)
        self.status_label.configure(bg=config.STATUSBAR_BG, fg=config.MUTED)

    def toggle_theme(self):
        config.toggle_theme()
        self._apply_bg()
        self._setup_styles()
        self._refresh_current_view()
        logger.info("Theme switched to %s", config.current_theme)

    def _refresh_current_view(self):
        v = self._current_view
        self._current_view = None
        if v == "login":
            self.show_login()
        elif v == "register":
            self.show_register()
        elif v == "dashboard":
            self.show_dashboard()
        elif v == "form":
            self.show_form(self._form_sub_row)
        elif v == "chart":
            self.show_charts()
        elif v == "budget":
            self.show_budget()
        elif v == "profile":
            self.show_profile()
        else:
            self.show_login()

    def show_login(self):
        self._clear_container()
        self._current_view = "login"
        self._update_status()
        LoginFrame(self.container, self, self.auth_ctrl).pack(fill=tk.BOTH, expand=True)

    def show_register(self):
        self._clear_container()
        self._current_view = "register"
        self._update_status()
        RegisterFrame(self.container, self, self.auth_ctrl).pack(fill=tk.BOTH, expand=True)

    def show_dashboard(self):
        self._clear_container()
        self._current_view = "dashboard"
        DashboardFrame(self.container, self, self.sub_ctrl).pack(fill=tk.BOTH, expand=True)
        self._update_status()

    def show_form(self, sub_row=None):
        self._clear_container()
        self._current_view = "form"
        self._form_sub_row = sub_row
        SubscriptionFormFrame(self.container, self, self.sub_ctrl, sub_row).pack(fill=tk.BOTH, expand=True)
        self._update_status()

    def show_charts(self):
        self._clear_container()
        self._current_view = "chart"
        ChartFrame(self.container, self, self.sub_ctrl).pack(fill=tk.BOTH, expand=True)
        self._update_status()

    def show_budget(self):
        BudgetDialog(self, self, self.budget_ctrl)

    def show_profile(self):
        self._clear_container()
        self._current_view = "profile"
        ProfileFrame(self.container, self, self.auth_ctrl).pack(fill=tk.BOTH, expand=True)
        self._update_status()

    def login_success(self, user_row):
        self.current_user = user_row
        logger.info("User logged in: %s", user_row["username"])
        self.show_dashboard()

    def logout(self):
        logger.info("User logged out")
        self.current_user = None
        self.show_login()

    def _restore_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _on_close(self):
        if self.notifier._tray_icon is not None:
            self.withdraw()
        else:
            self.notifier.stop()
            self.destroy()


def main():
    db.init_db()
    app = LangganankuApp()
    app.mainloop()


if __name__ == "__main__":
    main()
