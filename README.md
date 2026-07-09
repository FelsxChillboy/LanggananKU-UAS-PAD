# LanggananKu

Aplikasi desktop **pelacak langganan otomatis** berbasis Python & Tkinter.
Membantu memantau seluruh langganan berulang (streaming, cloud, gym, cicilan,
dll) dalam satu dashboard, lengkap dengan pengingat jatuh tempo, analisis
pengeluaran, serta kontrol budget per kategori.

## Fitur

- 🔐 **Multi-user** — setiap pengguna punya data langganan sendiri
- 📋 **CRUD lengkap** — nama, kategori, harga, siklus, tanggal, metode bayar, catatan
- 📊 **Dashboard** — total estimasi bulanan, langganan aktif, daftar jatuh tempo, status budget
- 🔍 **Cari & Filter** — search real-time, filter kategori/status, sortir klik header
- 📦 **Arsip** — nonaktifkan langganan tanpa hapus, tampilkan/sembunyikan
- 📈 **Grafik & Insight** — diagram batang & pie per kategori + insight otomatis
- 💰 **Budget per Kategori** — set limit bulanan, progress bar, peringatan jika over
- 🔔 **Reminder** — notifikasi desktop + system tray icon + daftar in-app
- 🌙 **Dark Mode** — toggle tema terang/gelap, tersimpan otomatis
- 👤 **Profil** — ganti nama & password
- 📤 **Export CSV** — backup data langganan ke file CSV
- ⌨️ **Shortcuts** — Ctrl+N (tambah), Ctrl+S (simpan), Ctrl+F (cari), Escape (kembali)
- 💾 **100% offline** — data tersimpan lokal di SQLite (`langgananku.db`)

## Cara Menjalankan (dari source code)

1. Pastikan Python 3.10+ terpasang.
2. Clone repositori:
   ```bash
   git clone https://github.com/FelsxChillboy/LanggananKu.git
   cd LanggananKu
   ```
3. Install dependency:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan aplikasi:
   ```bash
   python main.py
   ```
5. Daftar akun baru di layar login, lalu mulai tambahkan langganan.

> Catatan: `plyer` dan `pystray` bersifat opsional — jika tidak berhasil
> terpasang di platform tertentu, aplikasi tetap berjalan normal dan hanya
> mengandalkan reminder di dalam dashboard.

## Build ke .exe (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name LanggananKu --hidden-import matplotlib --hidden-import matplotlib.backends.backend_tkagg --hidden-import plyer --hidden-import pystray --hidden-import PIL --hidden-import PIL._tkinter_finder main.py
```

File `.exe` hasil build berada di folder `dist/`. Cukup double-click, tidak perlu Python terinstall.

## Struktur Proyek

```
langgananku/
├── main.py                    # Entry point AppController
├── config.py                  # Konstanta, tema dark/light dinamis
├── charts.py                  # Grafik matplotlib + insight otomatis
├── notifier.py                # Notifikasi desktop & system tray
│
├── controllers/
│   ├── auth_controller.py     # Login, register, update profil
│   ├── subscription_controller.py  # CRUD langganan + validasi
│   └── budget_controller.py   # Budget per kategori
│
├── models/
│   └── database.py            # Skema SQLite, context manager, PBKDF2
│
├── views/
│   ├── auth_view.py           # Halaman login & register
│   ├── sidebar_view.py        # Navigasi sidebar
│   ├── dashboard_view.py      # Dashboard utama + tabel + budget bar
│   ├── form_view.py           # Form tambah/edit langganan
│   ├── chart_view.py          # Halaman grafik
│   ├── budget_view.py         # Dialog atur budget
│   ├── profile_view.py        # Edit profil pengguna
│   └── toast.py               # Snackbar notification non-blocking
│
├── tests/
│   ├── test_database.py
│   ├── test_auth_controller.py
│   └── test_subscription_controller.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Teknologi

Python 3, Tkinter/ttk, SQLite3, matplotlib, plyer, pystray, PyInstaller, pytest.

## Testing

```bash
pytest tests/ -v
```
