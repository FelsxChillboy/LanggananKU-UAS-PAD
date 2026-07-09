# LanggananKu

Aplikasi desktop **pelacak langganan otomatis** berbasis Python & Tkinter.
Membantu memantau seluruh langganan berulang (streaming, cloud, gym, cicilan,
dll) dalam satu dashboard, lengkap dengan pengingat jatuh tempo dan analisis
pengeluaran otomatis — konsep yang lazim dipakai di negara maju (mis. Rocket
Money, Bobby) namun belum banyak versi lokalnya di Indonesia.

## Fitur

- 🔐 Autentikasi multi-user (password di-hash, tiap pengguna punya data sendiri)
- 📋 CRUD langganan (nama, kategori, harga, siklus, tanggal, metode bayar)
- 📊 Dashboard: total estimasi bulanan, langganan aktif, daftar akan jatuh tempo
- 🔔 Reminder ganda: daftar in-app + notifikasi desktop asli (system tray)
- 📈 Grafik batang & pie per kategori, dengan insight otomatis
- 💾 100% offline — data tersimpan lokal di SQLite (`langgananku.db`)

## Cara Menjalankan (dari source code)

1. Pastikan Python 3.10+ terpasang.
2. Install dependency:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi:
   ```bash
   python main.py
   ```
4. Daftar akun baru di layar login, lalu mulai tambahkan langganan.

> Catatan: `plyer` dan `pystray` bersifat opsional — jika tidak berhasil
> terpasang di platform tertentu, aplikasi tetap berjalan normal dan hanya
> mengandalkan reminder di dalam dashboard.

## Build ke .exe (Windows)

```bash
pyinstaller --noconfirm --onefile --windowed --name LanggananKu main.py
```

File `.exe` hasil build akan berada di folder `dist/`.

## Struktur Proyek

```
langgananku/
├── main.py          # Entry point, seluruh UI Tkinter (login, dashboard, form)
├── database.py       # Skema & akses SQLite (users, subscriptions)
├── charts.py          # Grafik matplotlib + insight otomatis
├── notifier.py        # Notifikasi desktop & ikon system tray
├── requirements.txt
└── README.md
```

## Teknologi

Python 3, Tkinter/ttk, SQLite3, matplotlib, plyer, pystray, PyInstaller.
