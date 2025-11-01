from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox,
    QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCompleter
)
from PyQt6.QtCore import Qt  # Jangan lupa untuk mengimpor Qt untuk case sensitivity
from app.database.db import get_connection
from datetime import datetime


class SalesWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.cart = []

        # ================== GAYA GLOBAL ==================
        self.setStyleSheet(""" 
            QWidget {
                font-family: Segoe UI, Roboto, Arial;
                font-size: 14px;
            }

            QLabel {
                font-weight: 500;
            }

            QPushButton {
                background-color: #2563eb;
                color: black;
                padding: 10px;
                border-radius: 8px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #1e40af;
            }

            QPushButton:pressed {
                background-color: #1d4ed8;
            }

            
            QTableWidget {
                border: 1px solid #e5e7eb;
                gridline-color: #e5e7eb;
                font-size: 13px;
            }

            QHeaderView::section {
                background-color: #253955;  /* Ubah warna latar belakang header */
                color: white;                /* Ubah warna teks header */
                padding: 6px;
                font-weight: bold;
                border: none;
            }
        """)

        # ================== LAYOUT UI ==================
        layout = QVBoxLayout()

        title = QLabel("💰 Transaksi Penjualan")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 12px;")
        layout.addWidget(title)

        card_layout = QVBoxLayout()
        card_layout.setSpacing(10)

        card = QWidget()
        card.setLayout(card_layout)
        card.setStyleSheet(""" 
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 14px;
        """)

        # Label dan Input untuk Produk & Jumlah (dalam baris yang sama)
        layout.addWidget(QLabel("Pilih Produk dan Qty:"))

        # Layout Horizontal untuk Produk dan Jumlah
        hbox_filter = QHBoxLayout()

        # Dropdown Produk (ComboBox)
        self.cmb_product = QComboBox()
        self.load_products()

        # Jumlah (SpinBox untuk jumlah produk)
        self.spin_qty = QSpinBox()
        self.spin_qty.setRange(1, 100)
        self.spin_qty.setValue(1)
        self.spin_qty.setToolTip("Masukkan jumlah pembelian")  # Tooltip untuk petunjuk

        # Menambahkan widget produk dan jumlah ke layout horizontal
        hbox_filter.addWidget(self.cmb_product)
        hbox_filter.addWidget(self.spin_qty)

        # Tombol tambah (Add to transaction button)
        btn_add = QPushButton("➕ Tambah ke Transaksi")
        btn_add.clicked.connect(self.add_transaction)
        card_layout.addLayout(hbox_filter)  # Menambahkan layout produk
        card_layout.addWidget(btn_add)

        layout.addWidget(card)

        # ================== TABEL ==================
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Produk", "Harga", "Jumlah", "Total", "Aksi"])
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("alternate-background-color: #f9fafb;")

        header = self.table.horizontalHeader()
        for col in range(5):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

        # ================== TOMBOL-TOMBOL ==================
        btn_save = QPushButton("💾 Simpan Transaksi")
        btn_back = QPushButton("⬅️ Kembali")

        btn_save.clicked.connect(self.save_transaction)
        btn_back.clicked.connect(self.go_back)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_save)
        hbox.addWidget(btn_back)
        layout.addLayout(hbox)

        self.setLayout(layout)

    def load_products(self):
        # Fungsi untuk memuat produk dari database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM products")
        self.products = cursor.fetchall()
        conn.close()

        self.cmb_product.clear()
        self.cmb_product.setEditable(True)  # Menambahkan editable mode

        product_names = [f"{p[1]} - Rp{p[2]:,.0f}" for p in self.products]
        for p in self.products:
            self.cmb_product.addItem(f"{p[1]} - Rp{p[2]:,.0f}", userData=p)

        # Menggunakan QCompleter untuk menyediakan kemampuan pencarian
        completer = QCompleter(product_names)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)  # Tidak membedakan huruf besar/kecil
        self.cmb_product.setCompleter(completer)  # Mengaktifkan completer pada combo box

    def add_transaction(self):
        # Fungsi untuk menambahkan produk ke dalam transaksi
        product = self.cmb_product.currentData()
        if not product:
            QMessageBox.warning(self, "Error", "Silakan pilih produk dulu.")
            return

        qty = self.spin_qty.value()
        total = product[2] * qty
        self.cart.append((product[0], product[1], product[2], qty, total))
        self.update_table()

    def update_table(self):
        # Fungsi untuk memperbarui tabel dengan produk yang telah ditambahkan
        self.table.setRowCount(len(self.cart))
        for i, (_, name, price, qty, total) in enumerate(self.cart):
            self.table.setItem(i, 0, QTableWidgetItem(name))
            self.table.setItem(i, 1, QTableWidgetItem(f"Rp {price:,.0f}"))
            self.table.setItem(i, 2, QTableWidgetItem(str(qty)))
            self.table.setItem(i, 3, QTableWidgetItem(f"Rp {total:,.0f}"))

            btn_del = QPushButton("Hapus")
            btn_del.setProperty("row_index", i)
            btn_del.clicked.connect(self.handle_remove_by_button)
            btn_del.setStyleSheet(""" 
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    padding: 5px;
                    margin:2px 5px;
                    border-radius: 6px;
                }
                QPushButton:hover { background-color: #dc2626; }
            """)
            self.table.setCellWidget(i, 4, btn_del)

    def handle_remove_by_button(self):
        # Fungsi untuk menghapus produk dari keranjang transaksi
        btn = self.sender()
        row = btn.property("row_index")

        del self.cart[row]
        self.update_table()

    def save_transaction(self):
        # Fungsi untuk menyimpan transaksi ke database
        if not self.cart:
            QMessageBox.warning(self, "Peringatan", "Tidak ada produk!")
            return

        conn = get_connection()
        cursor = conn.cursor()

        total_all = sum(item[4] for item in self.cart)
        sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("INSERT INTO sales (sale_date, total) VALUES (?, ?)", (sale_date, total_all))
        sale_id = cursor.lastrowid

        for pid, _, price, qty, _ in self.cart:
            cursor.execute(
                "INSERT INTO sales_items (sale_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
                (sale_id, pid, qty, price)
            )
            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, pid))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "✅ Sukses", "Transaksi disimpan!")
        self.cart.clear()
        self.update_table()

    def go_back(self):
        # Fungsi untuk kembali ke halaman utama
        self.main_window.show_dashboard()
