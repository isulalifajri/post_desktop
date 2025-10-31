from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime
import sys

from app.ui.product_window import ProductWindow
from app.ui.sales_window import SalesWindow
from app.ui.report_window import ReportWindow
from app.database.db import get_dashboard_stats


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💼 POS Desktop")
        self.setGeometry(300, 200, 720, 480)
        self.setStyleSheet("""
            QWidget {
                background-color: #f3f4f6;
                font-family: 'Segoe UI';
            }
        """)
        self.timer = None
        self.show_dashboard()

    def show_dashboard(self):
        """Tampilan dashboard utama"""
        if self.timer:
            self.timer.stop()

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # 🏷️ HEADER
        header_layout = QHBoxLayout()
        title = QLabel("📊 Dashboard POS Desktop")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #111827;")
        header_layout.addWidget(title)

        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("color: #6b7280; font-size: 13px;")
        header_layout.addWidget(self.clock_label, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(header_layout)

        # 🕒 Waktu real-time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

        # 📈 Chart Pendapatan 3 Bulan Terakhir
        self.show_recent_revenue_chart(layout)

        # 📊 Statistik Ringkas
        self.stats_layout = QHBoxLayout()
        self.update_stats_cards()
        layout.addLayout(self.stats_layout)

        # 🔁 Tombol Refresh
        btn_refresh = QPushButton("🔄 Refresh Data")
        btn_refresh.setFixedHeight(38)
        btn_refresh.clicked.connect(self.update_stats_cards)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        layout.addWidget(btn_refresh)

        # 🧭 Menu Navigasi
        menu_layout = QHBoxLayout()
        menu_layout.setSpacing(15)
        buttons = [
            ("🧾 Produk", self.open_products),
            ("💰 Transaksi", self.open_sales),
            ("📊 Laporan", self.open_reports),
            ("🚪 Keluar", self.close)
        ]

        for text, action in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(45)
            btn.clicked.connect(action)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1d4ed8;
                }
            """)
            menu_layout.addWidget(btn)

        layout.addLayout(menu_layout)

        # 🦶 FOOTER
        footer = QLabel(f"Built with Python {sys.version.split()[0]}  •  POS Desktop")
        footer.setStyleSheet("""
            color: #9ca3af;
            font-size: 12px;
            margin-top: 20px;
            border-top: 1px solid #e5e7eb;
            padding-top: 8px;
        """)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    # ==========================================================
    # 📊 Chart Pendapatan 3 Bulan Terakhir
    # ==========================================================
    def show_recent_revenue_chart(self, layout):
        import matplotlib
        matplotlib.use('Agg')
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        import matplotlib.pyplot as plt
        from app.database.db import get_last_3_months_revenue

        data = get_last_3_months_revenue()
        if not data:
            chart_label = QLabel("📉 Belum ada data pendapatan 3 bulan terakhir.")
            chart_label.setStyleSheet("color: #6b7280; font-size: 13px;")
            layout.addWidget(chart_label)
            return

        months = [m for m, _ in data]
        totals = [t for _, t in data]

        fig, ax = plt.subplots(figsize=(5.5, 3))
        bars = ax.bar(months, totals, color="#4ade80")

        ax.set_title("Pendapatan 3 Bulan Terakhir", fontsize=11, pad=10)
        ax.set_ylabel("Total Pendapatan (Rp)")
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.4)

        fig.tight_layout()
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)

    # ==========================================================
    # 🕒 Update waktu real-time
    # ==========================================================
    def update_clock(self):
        if not hasattr(self, "clock_label"):
            return
        now = datetime.now().strftime("%A, %d %B %Y  %H:%M:%S")
        self.clock_label.setText(now)

    # ==========================================================
    # 📈 Statistik Dashboard
    # ==========================================================
    def update_stats_cards(self):
        from PyQt6.QtWidgets import QVBoxLayout
        stats = get_dashboard_stats()

        for i in reversed(range(self.stats_layout.count())):
            widget = self.stats_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        stat_cards = [
            ("📦 Jumlah Produk", str(stats["products"])),
            ("💰 Transaksi Hari Ini", str(stats["sales_today"])),
            ("💵 Pendapatan", f"Rp {int(stats['revenue_today']):,}".replace(",", ".")),
        ]

        for label, value in stat_cards:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border-radius: 16px;
                    border: 1px solid #e5e7eb;
                    padding: 18px;
                }
                QFrame:hover {
                    background-color: #f9fafb;
                }
            """)
            vbox = QVBoxLayout()
            l1 = QLabel(label)
            l1.setStyleSheet("color: #6b7280; font-weight: 600;")
            l2 = QLabel(value)
            l2.setStyleSheet("font-size: 20px; font-weight: bold; color: #2563eb;")
            vbox.addWidget(l1)
            vbox.addWidget(l2)
            card.setLayout(vbox)
            self.stats_layout.addWidget(card)

    # ==========================================================
    # 🚀 Navigasi antar halaman
    # ==========================================================
    def open_products(self):
        if self.timer:
            self.timer.stop()
        self.product_window = ProductWindow(self)
        self.setCentralWidget(self.product_window)

    def open_sales(self):
        if self.timer:
            self.timer.stop()
        self.sales_window = SalesWindow(self)
        self.setCentralWidget(self.sales_window)

    def open_reports(self):
        if self.timer:
            self.timer.stop()
        self.report_window = ReportWindow(self)
        self.setCentralWidget(self.report_window)
