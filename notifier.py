import threading
import time
import datetime
import logging
from PIL import Image, ImageDraw

from models import database as db
import config

try:
    from plyer import notification as desktop_notification
    HAS_PLYER = True
except Exception:
    HAS_PLYER = False

try:
    import pystray
    HAS_PYSTRAY = True
except Exception:
    HAS_PYSTRAY = False

logger = logging.getLogger(__name__)


def _buat_ikon_tray():
    img = Image.new("RGB", (64, 64), (58, 110, 224))
    d = ImageDraw.Draw(img)
    d.ellipse((10, 10, 54, 54), fill="white")
    d.text((22, 20), "L", fill=(58, 110, 224))
    return img


class NotifierService:
    def __init__(self, get_current_user_id_callback, on_open_window=None):
        self._get_user_id = get_current_user_id_callback
        self._on_open_window = on_open_window
        self._already_notified_today = set()
        self._stop_flag = threading.Event()
        self._tray_icon = None

    def start_background_checks(self):
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()
        logger.debug("Background notifier started")

    def _loop(self):
        while not self._stop_flag.is_set():
            self._check_and_notify()
            self._stop_flag.wait(config.CHECK_INTERVAL_SECONDS)

    def _check_and_notify(self):
        user_id = self._get_user_id()
        if not user_id:
            return
        try:
            upcoming = db.langganan_akan_jatuh_tempo(user_id, dalam_hari=config.NOTIF_DAYS_AHEAD)
            today_key = datetime.date.today().isoformat()
            for sub in upcoming:
                key = f"{today_key}-{sub['id']}"
                if key in self._already_notified_today:
                    continue
                self._already_notified_today.add(key)
                self._send_desktop_notification(sub)
        except Exception:
            logger.exception("Error in notifier check")

    def _send_desktop_notification(self, sub):
        title = "LanggananKu - Segera Jatuh Tempo"
        harga_fmt = f"Rp {sub['harga']:,.0f}".replace(",", ".")
        message = f"{sub['nama']} ({harga_fmt}) jatuh tempo pada {sub['tanggal_jatuh_tempo']}"
        if HAS_PLYER:
            try:
                desktop_notification.notify(title=title, message=message, timeout=8)
                return
            except Exception:
                logger.warning("Plyer notification failed, falling back to console")
        logger.info("NOTIFIKASI: %s - %s", title, message)

    def notify_now(self, title, message):
        if HAS_PLYER:
            try:
                desktop_notification.notify(title=title, message=message, timeout=6)
                return
            except Exception:
                pass
        logger.info("NOTIFIKASI: %s - %s", title, message)

    def start_tray_icon(self):
        if not HAS_PYSTRAY:
            return

        def on_open(icon, item):
            if self._on_open_window:
                self._on_open_window()

        def on_quit(icon, item):
            icon.stop()
            self._stop_flag.set()

        menu = pystray.Menu(
            pystray.MenuItem("Buka LanggananKu", on_open, default=True),
            pystray.MenuItem("Keluar", on_quit),
        )
        self._tray_icon = pystray.Icon("langgananku", _buat_ikon_tray(), "LanggananKu", menu)
        t = threading.Thread(target=self._tray_icon.run, daemon=True)
        t.start()
        logger.debug("System tray icon started")

    def stop(self):
        self._stop_flag.set()
        if self._tray_icon:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
