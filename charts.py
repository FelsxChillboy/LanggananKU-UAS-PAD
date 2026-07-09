import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import config


def buat_frame_grafik(parent, per_kategori: dict, jumlah_aktif: int) -> tk.Frame:
    frame = tk.Frame(parent, bg=config.CHART_INSIGHT_BG)

    fig = Figure(figsize=(7.2, 4.6), dpi=100, facecolor=config.CHART_FACE)
    ax_bar = fig.add_subplot(1, 2, 1)
    ax_pie = fig.add_subplot(1, 2, 2)

    ax_bar.set_facecolor(config.CHART_FACE)
    ax_pie.set_facecolor(config.CHART_FACE)

    ax_bar.tick_params(axis="x", colors=config.CHART_TEXT, labelsize=7)
    ax_bar.tick_params(axis="y", colors=config.CHART_TEXT, labelsize=7)
    ax_bar.spines["bottom"].set_color(config.CHART_AXIS)
    ax_bar.spines["left"].set_color(config.CHART_AXIS)
    ax_bar.spines["top"].set_visible(False)
    ax_bar.spines["right"].set_visible(False)

    if per_kategori:
        kategori = list(per_kategori.keys())
        nilai = list(per_kategori.values())
        colors = [config.CHART_COLORS[i % len(config.CHART_COLORS)] for i in range(len(kategori))]

        ax_bar.bar(kategori, nilai, color=colors)
        ax_bar.set_title("Pengeluaran per Kategori (estimasi/bulan)", fontsize=9, color=config.CHART_TEXT)

        ax_pie.pie(nilai, labels=kategori, autopct="%1.0f%%", colors=colors,
                   textprops={"fontsize": 7, "color": config.CHART_TEXT})
        ax_pie.set_title("Proporsi Pengeluaran", fontsize=9, color=config.CHART_TEXT)
    else:
        ax_bar.text(0.5, 0.5, "Belum ada data langganan aktif",
                    ha="center", va="center", transform=ax_bar.transAxes, color=config.CHART_TEXT)
        ax_pie.axis("off")

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    insight_text = buat_insight(per_kategori, jumlah_aktif)
    insight_label = tk.Label(
        frame, text=insight_text, bg=config.CHART_INSIGHT_BG, fg=config.DARK,
        font=(config.FONT_FAMILY, 10), wraplength=680, justify="left", padx=14, pady=10,
        relief=tk.FLAT,
    )
    insight_label.pack(fill=tk.X, padx=10, pady=(6, 10))

    return frame


def buat_insight(per_kategori: dict, jumlah_aktif: int) -> str:
    total = sum(per_kategori.values())
    if total == 0:
        return "\U0001f4a1 Insight: Belum ada langganan aktif untuk dianalisis. Tambahkan langganan pertamamu di menu 'Tambah Baru'."

    kategori_tertinggi = max(per_kategori, key=per_kategori.get)
    persen_tertinggi = (per_kategori[kategori_tertinggi] / total) * 100
    rata_rata = total / jumlah_aktif if jumlah_aktif else 0

    total_fmt = f"Rp {total:,.0f}".replace(",", ".")
    rata_fmt = f"Rp {rata_rata:,.0f}".replace(",", ".")

    pesan = (
        f"\U0001f4a1 Insight: Estimasi total pengeluaran langganan bulan ini sekitar {total_fmt}, "
        f"berasal dari {jumlah_aktif} langganan aktif (rata-rata {rata_fmt}/langganan). "
        f"Kategori '{kategori_tertinggi}' mendominasi sekitar {persen_tertinggi:.0f}% dari total pengeluaran"
    )
    if persen_tertinggi > 50:
        pesan += " \u2014 pertimbangkan untuk meninjau kembali langganan di kategori ini agar pengeluaran lebih seimbang."
    else:
        pesan += "."
    return pesan
