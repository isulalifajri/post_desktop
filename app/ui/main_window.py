from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from datetime import datetime
from app.ui.product_window import ProductWindow
from app.ui.sales_window import SalesWindow
from app.ui.report_window import ReportWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💼 POS Desktop")
        self.setGeometry(300, 200, 500, 400)
        self.show_dashboard()

    def show_dashboard(self):
        """Tampilan dashboard utama"""
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 🌤️ Judul dan waktu
        title = QLabel("Dashboard POS Desktop")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #111827;")

        subtitle = QLabel(f"Hari ini: {datetime.now().strftime('%A, %d %B %Y')}")
        subtitle.setStyleSheet("color: #6b7280; font-size: 13px; margin-bottom: 10px;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # 📊 Statistik ringkas
        stats_layout = QHBoxLayout()

        stat_cards = [
            ("📦 Jumlah Produk", "120"),
            ("💰 Transaksi Hari Ini", "35"),
            ("💵 Pendapatan", "Rp 12.500.000"),
        ]

        for label, value in stat_cards:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border-radius: 10px;
                    border: 1px solid #e5e7eb;
                    padding: 12px;
                }
                QLabel {
                    font-size: 13px;
                }
            """)
            vbox = QVBoxLayout()
            l1 = QLabel(label)
            l1.setStyleSheet("color: #6b7280; font-weight: 500;")
            l2 = QLabel(value)
            l2.setStyleSheet("font-size: 16px; font-weight: bold; color: #2563eb;")
            vbox.addWidget(l1)
            vbox.addWidget(l2)
            card.setLayout(vbox)
            stats_layout.addWidget(card)

        layout.addLayout(stats_layout)

        # 🔘 Tombol menu
        menu_layout = QHBoxLayout()
        menu_layout.setSpacing(10)
        buttons = [
            ("🧾 Produk", self.open_products),
            ("💰 Transaksi", self.open_sales),
            ("📊 Laporan", self.open_reports),
            ("🚪 Keluar", self.close)
        ]

        for text, action in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.clicked.connect(action)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1e40af;
                }
            """)
            menu_layout.addWidget(btn)

        layout.addLayout(menu_layout)

        # 🌈 Set background dan font global
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #f9fafb;
                font-family: 'Segoe UI';
            }
        """)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_products(self):
        self.product_window = ProductWindow(self)
        self.setCentralWidget(self.product_window)

    def open_sales(self):
        self.sales_window = SalesWindow(self)
        self.setCentralWidget(self.sales_window)

    def open_reports(self):
        self.report_window = ReportWindow(self)
        self.setCentralWidget(self.report_window)
