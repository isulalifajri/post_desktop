from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QDialog,
    QLineEdit, QFormLayout, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from app.database.db import get_connection

class ProductWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Layout utama
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Judul
        title = QLabel("🧾 Daftar Produk")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # ------------------------
        # Pencarian Produk Real-time
        # ------------------------
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari produk berdasarkan nama...")
        self.search_input.setStyleSheet("padding: 8px; font-size: 16px;")
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Trigger pencarian real-time
        self.search_input.textChanged.connect(self.search_product)

        # ------------------------
        # Tabel Produk
        # ------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Tambah kolom aksi
        self.table.setHorizontalHeaderLabels(["No", "Nama", "Harga", "Stok", "Aksi"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 17px;
                border: 1px solid #34495e;
                border-radius: 10px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:alternate {
                background-color: #ecf0f1; 
            }
            QTableWidget::item {
                background-color: #ffffff; 
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-size:18px;
                font-weight: bold;
                border: 1px solid #2c3e50;
            }
        """)
        layout.addWidget(self.table)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # No
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)           # Nama
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Harga
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)           # Stok
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)           # Aksi

        # Tombol tambah dan kembali
        button_layout = QHBoxLayout()
        btn_add = QPushButton("Tambah Produk")
        btn_add.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold;")
        btn_back = QPushButton("Kembali ke Menu")
        btn_back.setStyleSheet("background-color: #c0392b; color: white; padding: 10px; font-weight: bold;")
        btn_add.clicked.connect(self.open_add_product)
        btn_back.clicked.connect(self.go_back)
        button_layout.addWidget(btn_add)
        button_layout.addWidget(btn_back)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.load_products()

    # ==========================================
    # LOAD DATA PRODUK
    # ==========================================
    def load_products(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, stock FROM products")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            # Set tinggi baris
            self.table.setRowHeight(i, 50)

            # No urut manual
            no_item = QTableWidgetItem(str(i + 1))
            no_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, no_item)

            # Data lainnya
            for j, value in enumerate(row[1:], start=1):  # skip id asli
                if j == 2:  # kolom Harga
                    value_str = f"Rp {int(value):,}".replace(",", ".")
                    item = QTableWidgetItem(value_str)
                else:
                    item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)

            # Kolom aksi (Edit & Hapus) diperbesar
            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("""
                background-color: #2980b9;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            """)
            btn_edit.clicked.connect(lambda checked, r=i: self.open_edit_product(r))

            btn_delete = QPushButton("Hapus")
            btn_delete.setStyleSheet("""
                background-color: #e74c3c;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            """)
            btn_delete.clicked.connect(lambda checked, r=i: self.delete_product(r))

            action_layout = QHBoxLayout()
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            action_widget.setStyleSheet("background-color: transparent;")
            self.table.setCellWidget(i, 4, action_widget)

    # ==========================================
    # PENCARIAN REAL-TIME
    # ==========================================
    def search_product(self):
        query = self.search_input.text().lower()
        for i in range(self.table.rowCount()):
            item = self.table.item(i, 1)  # kolom Nama Produk
            if query in item.text().lower():
                self.table.setRowHidden(i, False)
            else:
                self.table.setRowHidden(i, True)

    # ==========================================
    # TAMBAH PRODUK
    # ==========================================
    def open_add_product(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Tambah Produk")
        form_layout = QFormLayout(dialog)

        input_name = QLineEdit()
        input_price = QLineEdit()
        input_price.setPlaceholderText("contoh: 12000")
        input_stock = QLineEdit()
        input_stock.setPlaceholderText("contoh: 10")

        form_layout.addRow("Nama Produk:", input_name)
        form_layout.addRow("Harga:", input_price)
        form_layout.addRow("Stok:", input_stock)

        btn_save = QPushButton("Simpan")
        btn_cancel = QPushButton("Batal")
        btn_save.clicked.connect(lambda: self.save_product(dialog, input_name.text(), input_price.text(), input_stock.text()))
        btn_cancel.clicked.connect(dialog.reject)
        form_layout.addRow(btn_save, btn_cancel)
        dialog.exec()

    def save_product(self, dialog, name, price, stock):
        if not name or not price:
            QMessageBox.warning(self, "Error", "Nama dan harga tidak boleh kosong!")
            return
        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            QMessageBox.warning(self, "Error", "Harga dan stok harus berupa angka!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Sukses", f"Produk '{name}' berhasil ditambahkan.")
        dialog.accept()
        self.load_products()

    # ==========================================
    # EDIT PRODUK
    # ==========================================
    def open_edit_product(self, row_index):
        product_id = row_index + 1  # nomor urut manual
        old_name = self.table.item(row_index, 1).text()
        old_price = self.table.item(row_index, 2).text()
        old_stock = self.table.item(row_index, 3).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Produk")
        form_layout = QFormLayout(dialog)

        input_name = QLineEdit(old_name)
        input_price = QLineEdit(old_price)
        input_stock = QLineEdit(old_stock)

        form_layout.addRow("Nama Produk:", input_name)
        form_layout.addRow("Harga:", input_price)
        form_layout.addRow("Stok:", input_stock)

        btn_update = QPushButton("Simpan Perubahan")
        btn_cancel = QPushButton("Batal")
        btn_update.clicked.connect(lambda: self.update_product(dialog, product_id, input_name.text(), input_price.text(), input_stock.text()))
        btn_cancel.clicked.connect(dialog.reject)
        form_layout.addRow(btn_update, btn_cancel)
        dialog.exec()

    def update_product(self, dialog, product_id, name, price, stock):
        if not name or not price:
            QMessageBox.warning(self, "Error", "Nama dan harga tidak boleh kosong!")
            return
        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            QMessageBox.warning(self, "Error", "Harga dan stok harus berupa angka!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET name = ?, price = ?, stock = ? WHERE id = ?", (name, price, stock, product_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Sukses", f"Produk '{name}' berhasil diperbarui.")
        dialog.accept()
        self.load_products()

    # ==========================================
    # HAPUS PRODUK
    # ==========================================
    def delete_product(self, row_index):
        product_id = row_index + 1
        product_name = self.table.item(row_index, 1).text()

        confirm = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Yakin ingin menghapus produk '{product_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Sukses", f"Produk '{product_name}' telah dihapus.")
            self.load_products()

    # ==========================================
    # KEMBALI KE MENU UTAMA
    # ==========================================
    def go_back(self):
        self.main_window.show_dashboard()
