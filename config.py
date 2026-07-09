import os
import json

import sys

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "langgananku.db")
LOG_PATH = os.path.join(BASE_DIR, "langgananku.log")
THEME_FILE = os.path.join(BASE_DIR, ".theme.json")

APP_TITLE = "LanggananKu - Pelacak Langganan Otomatis"
APP_GEOMETRY = "980x640"
APP_MIN_WIDTH = 880
APP_MIN_HEIGHT = 580

FONT_FAMILY = "Segoe UI"

ICON_HOUSE = "\U0001f3e0"
ICON_PLUS = "\u2795"
ICON_CHART = "\U0001f4ca"
ICON_DOOR = "\U0001f6aa"
ICON_MONEY = "\U0001f4b0"
ICON_LIST = "\U0001f4cb"
ICON_CLOCK = "\u23f0"
ICON_USER = "\U0001f464"
ICON_CHECK = "\u2705"
ICON_LOCK = "\U0001f512"
ICON_SAVE = "\U0001f4be"
ICON_CLOSE = "\u274c"
ICON_WARN = "\u26a0\ufe0f"
ICON_GEAR = "\u2699\ufe0f"
ICON_BELL = "\U0001f514"
ICON_WALLET = "\U0001f9fe"
ICON_MAIL = "\u2709\ufe0f"
ICON_SEARCH = "\U0001f50d"
ICON_ARCHIVE = "\U0001f4e6"
ICON_REFRESH = "\U0001f504"
ICON_FILTER = "\U0001f3b2"
ICON_BUDGET = "\U0001f4b8"
ICON_PROFILE = "\U0001f464"
ICON_EDIT = "\u270f\ufe0f"
ICON_KEY = "\U0001f511"

KATEGORI_LIST = ["Hiburan", "Produktivitas", "Kesehatan", "Pendidikan", "Keuangan", "Lainnya"]
SIKLUS_LIST = ["Mingguan", "Bulanan", "Tahunan"]
SIKLUS_HARI = {"Mingguan": 7, "Bulanan": 30, "Tahunan": 365}

CHART_COLORS_LIGHT = ["#3A6EE0", "#5AAA6E", "#E6BE3C", "#E05A5A", "#8A6FE0", "#3CBFC2", "#E08A3C"]
CHART_COLORS_DARK = ["#5B8DEF", "#81C784", "#FFD54F", "#EF5350", "#B39DDB", "#4DD0E1", "#FF8A65"]

CHECK_INTERVAL_SECONDS = 60 * 30
NOTIF_DAYS_AHEAD = 3

_LIGHT = {
    "ACCENT": "#3A6EE0",
    "ACCENT_HOVER": "#2F58B5",
    "ACCENT_LIGHT": "#E8EEFB",
    "DARK": "#282A30",
    "MUTED": "#6B6E80",
    "BG": "#F5F6F8",
    "DANGER": "#E05A5A",
    "DANGER_HOVER": "#C94D4D",
    "DANGER_LIGHT": "#FDE8E8",
    "OK": "#3AAA6E",
    "OK_HOVER": "#32975F",
    "OK_LIGHT": "#E8F5EE",
    "WARNING": "#E0A63C",
    "WARNING_LIGHT": "#FCF3DD",
    "SIDEBAR_BG": "#FFFFFF",
    "SIDEBAR_ACTIVE_BG": "#E2E9FA",
    "SIDEBAR_ACTIVE_FG": "#3A6EE0",
    "SIDEBAR_HOVER_BG": "#F0F2F5",
    "CARD_BG": "#FFFFFF",
    "CARD_BORDER": "#D0D3D9",
    "INPUT_BG": "#F8F9FA",
    "TABLE_ALT_ROW": "#F8F9FA",
    "TABLE_SELECTED_BG": "#3A6EE0",
    "CHART_INSIGHT_BG": "#EEF2FB",
    "STATUSBAR_BG": "#F0F2F5",
    "TOGGLE_BG": "#E8EEFB",
    "TOGGLE_FG": "#3A6EE0",
    "CHART_COLORS": CHART_COLORS_LIGHT,
    "CHART_FACE": "#FFFFFF",
    "CHART_AXIS": "#D0D3D9",
    "CHART_TEXT": "#282A30",
}

_DARK = {
    "ACCENT": "#5B8DEF",
    "ACCENT_HOVER": "#7AA3F2",
    "ACCENT_LIGHT": "#2D3A5C",
    "DARK": "#E0E0E0",
    "MUTED": "#9E9E9E",
    "BG": "#1A1A2E",
    "DANGER": "#EF5350",
    "DANGER_HOVER": "#E57373",
    "DANGER_LIGHT": "#3D2020",
    "OK": "#66BB6A",
    "OK_HOVER": "#81C784",
    "OK_LIGHT": "#1E3A20",
    "WARNING": "#FFA726",
    "WARNING_LIGHT": "#3D2E14",
    "SIDEBAR_BG": "#1E1E38",
    "SIDEBAR_ACTIVE_BG": "#2D3A5C",
    "SIDEBAR_ACTIVE_FG": "#5B8DEF",
    "SIDEBAR_HOVER_BG": "#252548",
    "CARD_BG": "#1E1E38",
    "CARD_BORDER": "#3A3A5C",
    "INPUT_BG": "#1A1A2E",
    "TABLE_ALT_ROW": "#252548",
    "TABLE_SELECTED_BG": "#2D3A5C",
    "CHART_INSIGHT_BG": "#1E2A3D",
    "STATUSBAR_BG": "#1E1E38",
    "TOGGLE_BG": "#2D3A5C",
    "TOGGLE_FG": "#5B8DEF",
    "CHART_COLORS": CHART_COLORS_DARK,
    "CHART_FACE": "#1E1E38",
    "CHART_AXIS": "#3A3A5C",
    "CHART_TEXT": "#E0E0E0",
}

current_theme = "light"


def __getattr__(name):
    colors = _DARK if current_theme == "dark" else _LIGHT
    if name in colors:
        return colors[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def set_theme(mode: str):
    global current_theme
    current_theme = mode
    _save_theme(mode)


def toggle_theme() -> str:
    new = "dark" if current_theme == "light" else "light"
    set_theme(new)
    return new


def load_theme():
    try:
        with open(THEME_FILE, encoding="utf-8") as f:
            data = json.load(f)
            if data.get("theme") in ("light", "dark"):
                set_theme(data["theme"])
    except (FileNotFoundError, json.JSONDecodeError):
        pass


def _save_theme(mode: str):
    try:
        with open(THEME_FILE, "w", encoding="utf-8") as f:
            json.dump({"theme": mode}, f)
    except OSError:
        pass
