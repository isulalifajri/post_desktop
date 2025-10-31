from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from app.ui.product_window import ProductWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("POS Desktop")
        self.setGeometry(300, 200, 400, 300)
        self.show_menu()  # panggil tampilan menu utama pertama kali

    def show_menu(self):
        """Tampilkan menu utama"""
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Judul
        title = QLabel("💼 POS Desktop")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title)

        # Tombol menu
        btn_products = QPushButton("🧾 Produk")
        btn_sales = QPushButton("💰 Transaksi")
        btn_reports = QPushButton("📊 Laporan")
        btn_exit = QPushButton("⚙️ Keluar")

        # Aksi tombol
        btn_products.clicked.connect(self.open_products)
        btn_exit.clicked.connect(self.close)

        # Tambahkan semua tombol ke layout
        for btn in [btn_products, btn_sales, btn_reports, btn_exit]:
            btn.setFixedHeight(40)
            layout.addWidget(btn)

        # Pasang layout ke widget tengah
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_products(self):
        """Buka halaman produk"""
        self.product_window = ProductWindow(self)
        self.setCentralWidget(self.product_window)
