from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem
)
from app.database.db import get_connection
from datetime import datetime


class SalesWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        title = QLabel("💰 Transaksi Penjualan")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Pilih produk
        self.cmb_product = QComboBox()
        self.load_products()
        layout.addWidget(QLabel("Pilih Produk:"))
        layout.addWidget(self.cmb_product)

        # Input jumlah
        layout.addWidget(QLabel("Jumlah:"))
        self.spin_qty = QSpinBox()
        self.spin_qty.setRange(1, 100)
        layout.addWidget(self.spin_qty)

        # Tombol tambah transaksi
        btn_add = QPushButton("Tambah ke Transaksi")
        btn_add.clicked.connect(self.add_transaction)
        layout.addWidget(btn_add)

        # Tabel daftar transaksi sementara
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Produk", "Harga", "Jumlah", "Total"])
        layout.addWidget(self.table)

        # Tombol simpan & kembali
        btn_save = QPushButton("💾 Simpan Transaksi")
        btn_back = QPushButton("⬅️ Kembali ke Menu")

        btn_save.clicked.connect(self.save_transaction)
        btn_back.clicked.connect(self.go_back)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_save)
        hbox.addWidget(btn_back)
        layout.addLayout(hbox)

        self.setLayout(layout)
        self.cart = []  # keranjang sementara

    def load_products(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM products")
        self.products = cursor.fetchall()
        conn.close()

        self.cmb_product.clear()
        for p in self.products:
            self.cmb_product.addItem(f"{p[1]} - Rp{p[2]:,.0f}", userData=p)

    def add_transaction(self):
        """Tambahkan produk ke tabel transaksi"""
        product = self.cmb_product.currentData()
        qty = self.spin_qty.value()
        total = product[2] * qty

        self.cart.append((product[0], product[1], product[2], qty, total))
        self.update_table()

    def update_table(self):
        self.table.setRowCount(len(self.cart))
        for i, (_, name, price, qty, total) in enumerate(self.cart):
            self.table.setItem(i, 0, QTableWidgetItem(name))
            self.table.setItem(i, 1, QTableWidgetItem(str(price)))
            self.table.setItem(i, 2, QTableWidgetItem(str(qty)))
            self.table.setItem(i, 3, QTableWidgetItem(str(total)))

    def save_transaction(self):
        """Simpan semua transaksi ke database"""
        conn = get_connection()
        cursor = conn.cursor()

        for pid, _, price, qty, total in self.cart:
            cursor.execute("""
                INSERT INTO sales (product_id, quantity, total, sale_date)
                VALUES (?, ?, ?, ?)
            """, (pid, qty, total, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

            # Kurangi stok produk
            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, pid))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Sukses", "Transaksi berhasil disimpan!")
        self.cart.clear()
        self.update_table()

    def go_back(self):
        self.main_window.show_dashboard()
