import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox,
    QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, 
    QCompleter, QInputDialog, QDialog, QLineEdit 
)
from PyQt6.QtCore import Qt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
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
                background-color: #253955;
                color: white;
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
        self.spin_qty.setToolTip("Masukkan jumlah pembelian")

        # Menambahkan widget produk dan jumlah ke layout horizontal
        hbox_filter.addWidget(self.cmb_product)
        hbox_filter.addWidget(self.spin_qty)

        # Tombol tambah (Add to transaction button)
        btn_add = QPushButton("➕ Tambah ke Transaksi")
        btn_add.clicked.connect(self.add_transaction)
        card_layout.addLayout(hbox_filter)
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

        # ================== TOMBOL ==================
        btn_save_and_print = QPushButton("💾 Simpan & Cetak Transaksi")
        btn_back = QPushButton("⬅️ Kembali")

        btn_save_and_print.clicked.connect(self.save_and_print_transaction)
        btn_back.clicked.connect(self.go_back)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_save_and_print)
        hbox.addWidget(btn_back)
        layout.addLayout(hbox)

        self.setLayout(layout)

    def load_products(self):
        # Memuat produk dari database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM products")
        self.products = cursor.fetchall()
        conn.close()

        self.cmb_product.clear()
        self.cmb_product.setEditable(True)

        product_names = [f"{p[1]} - Rp{p[2]:,.0f}" for p in self.products]
        for p in self.products:
            self.cmb_product.addItem(f"{p[1]} - Rp{p[2]:,.0f}", userData=p)

        completer = QCompleter(product_names)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.cmb_product.setCompleter(completer)

    def add_transaction(self):
        # Menambahkan produk ke dalam transaksi
        product = self.cmb_product.currentData()
        if not product:
            QMessageBox.warning(self, "Error", "Silakan pilih produk dulu.")
            return

        qty = self.spin_qty.value()
        total = product[2] * qty
        self.cart.append((product[0], product[1], product[2], qty, total))
        self.update_table()

    def update_table(self):
        # Memperbarui tabel dengan produk yang telah ditambahkan
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
        # Menghapus produk dari keranjang transaksi
        btn = self.sender()
        row = btn.property("row_index")

        del self.cart[row]
        self.update_table()

    def save_and_print_transaction(self):
        # Menyimpan dan mencetak transaksi
        if not self.cart:
            QMessageBox.warning(self, "Peringatan", "Tidak ada produk untuk diproses!")
            return

        # Hitung total harga transaksi
        total_all = sum(item[4] for item in self.cart)

        # Tampilkan dialog untuk memasukkan jumlah uang yang dibayarkan
        payment_dialog = QDialog(self)
        payment_dialog.setWindowTitle("Jumlah Bayar")
        payment_dialog.setStyleSheet("""
            QDialog {
                background: #ffffff;
                border-radius: 12px;
                padding: 20px;
                min-width: 350px;
                max-width: 700px;
            }

            QLabel {
                font-size: 14px;
                font-weight: 500;
                color: #333;
                border-radius: 3px;
                padding: 3px;
                margin-bottom: 10px;
            }

            QLineEdit {
                padding: 12px;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
                font-size: 14px;
                margin-bottom: 20px;
                color: #333;
            }

            QLineEdit:focus {
                border: 1px solid #2563eb;
            }

            QLabel#change_label {
                font-size: 16px;
                font-weight: bold;
                padding:5px;
                border-radius:3px;
                color: #2563eb;
            }

            QPushButton {
                background-color: #2563eb;
                color: white;
                padding: 15px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                margin-top: 20px;
                width: 100%;
            }

            QPushButton:hover {
                background-color: #1e40af;
            }

            QPushButton:pressed {
                background-color: #1d4ed8;
            }

            QPushButton#btn_cancel {
                background-color: #ef4444;
            }

            QPushButton#btn_cancel:hover {
                background-color: #dc2626;
            }
        """)

        # Layout untuk input pembayaran
        layout = QVBoxLayout(payment_dialog)

        # Menampilkan daftar produk yang dibeli
        label_products = QLabel("Produk yang Dibeli:", payment_dialog)
        layout.addWidget(label_products)

        for item in self.cart:
            name, price, qty, total = item[1], item[2], item[3], item[4]
            product_label = QLabel(f"{name} - {qty} x Rp{price:,.0f} = Rp {total:,.0f}", payment_dialog)
            layout.addWidget(product_label)

        # Menampilkan total harga
        total_label = QLabel(f"Total Harga: Rp {total_all:,.0f}", payment_dialog)
        layout.addWidget(total_label)

        # Input jumlah uang yang dibayarkan
        input_payment = QLineEdit(payment_dialog)
        input_payment.setPlaceholderText("Masukkan Jumlah Bayar")
        layout.addWidget(input_payment)

        # Label untuk menampilkan kembalian
        self.change_label = QLabel("Kembalian: Rp 0", payment_dialog)
        self.change_label.setObjectName("change_label")
        layout.addWidget(self.change_label)

        # Membuat layout horizontal untuk tombol
        button_layout = QHBoxLayout()

        # Tombol simpan dan cetak
        btn_save_and_print = QPushButton("Simpan & Cetak", payment_dialog)
        btn_cancel = QPushButton("Batal", payment_dialog)
        btn_cancel.setObjectName("btn_cancel")

        # Set lebar tombol agar seragam
        btn_save_and_print.setFixedWidth(150)
        btn_cancel.setFixedWidth(150)

        # Menambahkan tombol ke dalam layout horizontal
        button_layout.addWidget(btn_save_and_print)
        button_layout.addWidget(btn_cancel)

        # Menambahkan layout tombol ke dalam layout utama
        layout.addLayout(button_layout)

        # Fungsi untuk menghitung dan menampilkan kembalian
        def update_change():
            try:
                amount_paid = float(input_payment.text().strip())
                if amount_paid >= total_all:
                    change = amount_paid - total_all
                    self.change_label.setText(f"Kembalian: Rp {change:,.0f}")
                else:
                    self.change_label.setText("Kembalian: Rp 0")
            except ValueError:
                self.change_label.setText("Kembalian: Rp 0")

        # Update kembalian setiap kali user mengetikkan jumlah bayar
        input_payment.textChanged.connect(update_change)

        # Fungsi saat tombol simpan dan cetak diklik
        def on_save_and_print():
            try:
                amount_paid = float(input_payment.text().strip())
            except ValueError:
                QMessageBox.warning(payment_dialog, "Error", "Input jumlah uang yang dibayarkan tidak valid.")
                return

            if amount_paid < total_all:
                QMessageBox.warning(payment_dialog, "Error", "Jumlah uang yang dibayarkan kurang dari total harga!")
                return

            # Hitung kembalian
            change = amount_paid - total_all
            # Simpan transaksi ke database
            conn = get_connection()
            cursor = conn.cursor()

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

            # Simpan PDF ke folder Downloads
            downloads_folder = Path(os.path.expanduser("~")) / "Downloads"
            pdf_filename = downloads_folder / f"transaksi_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            pdf = canvas.Canvas(str(pdf_filename), pagesize=letter)

            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(100, 750, "FRESH SHOPMART")
            pdf.setFont("Helvetica", 12)
            pdf.drawString(100, 735, "JL. BUKIT KEMBANG, KEL. KEMBANG, KEC. A, KOTA KANGEAN 13139")
            pdf.line(100, 730, 500, 730)

            pdf.drawString(100, 715, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            pdf.drawString(100, 700, f"Transaction No: {sale_id}")

            pdf.line(100, 695, 500, 695)

            y_position = 680
            total_amount = 0
            for item in self.cart:
                name, price, qty, total = item[1], item[2], item[3], item[4]
                pdf.drawString(100, y_position, f"{name} - {qty} x Rp{price:,.0f}")
                y_position -= 15
                pdf.drawString(100, y_position, f"Rp {total:,.0f}")
                y_position -= 20
                total_amount += total

            pdf.line(100, y_position, 500, y_position)

            # Detail pembayaran
            y_position -= 20
            pdf.drawString(100, y_position, f"Total: Rp {total_amount:,.0f}")
            pdf.drawString(100, y_position-15, f"Tunai: Rp {amount_paid:,.0f}")
            pdf.drawString(100, y_position-30, f"Kembalian: Rp {change:,.0f}")

            pdf.line(100, y_position-35, 500, y_position-35)

            # Pesan Terima Kasih
            pdf.drawString(100, y_position-50, "Terima kasih telah berbelanja di toko kami!")
            pdf.drawString(100, y_position-65, "Layanan Pelanggan: 0324324 | freshshop@gmail.com")

            pdf.save()

            QMessageBox.information(self, "Sukses", f"Transaksi berhasil disimpan dan dicetak! ({pdf_filename})")

            # Clear keranjang dan update tabel
            self.cart.clear()
            self.update_table()
            payment_dialog.accept()

        btn_save_and_print.clicked.connect(on_save_and_print)
        btn_cancel.clicked.connect(payment_dialog.reject)

        payment_dialog.exec()


    # ==================================================
    # KEMBALI KE DASHBOARD
    # ==================================================
    def go_back(self):
        self.main_window.show_dashboard()
