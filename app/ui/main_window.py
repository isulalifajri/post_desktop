from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("POS Desktop")
        self.setGeometry(300, 200, 400, 300)

        # Widget utama
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Judul
        title = QLabel("💼 POS Desktop")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title)

        # Tombol-tombol menu
        btn_products = QPushButton("🧾 Produk")
        btn_sales = QPushButton("💰 Transaksi")
        btn_reports = QPushButton("📊 Laporan")
        btn_exit = QPushButton("⚙️ Keluar")

        # Tambahkan ke layout
        for btn in [btn_products, btn_sales, btn_reports, btn_exit]:
            btn.setFixedHeight(40)
            layout.addWidget(btn)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
