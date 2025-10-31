from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QDialog,
    QLineEdit, QFormLayout, QMessageBox
)
from app.database.db import get_connection


class ProductWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()

        title = QLabel("🧾 Daftar Produk")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Tabel produk
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Nama", "Harga"])
        layout.addWidget(self.table)

        # Tombol-tombol
        button_layout = QHBoxLayout()
        btn_add = QPushButton("Tambah Produk")
        btn_edit = QPushButton("Edit Produk")
        btn_delete = QPushButton("Hapus Produk")
        btn_back = QPushButton("Kembali ke Menu")

        btn_add.clicked.connect(self.open_add_product)
        btn_edit.clicked.connect(self.open_edit_product)
        btn_delete.clicked.connect(self.delete_product)
        btn_back.clicked.connect(self.go_back)

        button_layout.addWidget(btn_add)
        button_layout.addWidget(btn_edit)
        button_layout.addWidget(btn_delete)
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
        cursor.execute("SELECT id, name, price FROM products")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

    # ==========================================
    # TAMBAH PRODUK BARU
    # ==========================================
    def open_add_product(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Tambah Produk")
        form_layout = QFormLayout(dialog)

        input_name = QLineEdit()
        input_price = QLineEdit()
        input_price.setPlaceholderText("contoh: 12000")

        form_layout.addRow("Nama Produk:", input_name)
        form_layout.addRow("Harga:", input_price)

        btn_save = QPushButton("Simpan")
        btn_cancel = QPushButton("Batal")

        btn_save.clicked.connect(lambda: self.save_product(dialog, input_name.text(), input_price.text()))
        btn_cancel.clicked.connect(dialog.reject)

        form_layout.addRow(btn_save, btn_cancel)

        dialog.exec()

    def save_product(self, dialog, name, price):
        if not name or not price:
            QMessageBox.warning(self, "Error", "Nama dan harga tidak boleh kosong!")
            return

        try:
            price = float(price)
        except ValueError:
            QMessageBox.warning(self, "Error", "Harga harus berupa angka!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, 0)", (name, price))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Sukses", f"Produk '{name}' berhasil ditambahkan.")
        dialog.accept()
        self.load_products()

    # ==========================================
    # EDIT PRODUK
    # ==========================================
    def open_edit_product(self):
        """Buka form edit produk"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Pilih produk yang ingin diedit terlebih dahulu.")
            return

        product_id = self.table.item(selected_row, 0).text()
        old_name = self.table.item(selected_row, 1).text()
        old_price = self.table.item(selected_row, 2).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Produk")
        form_layout = QFormLayout(dialog)

        input_name = QLineEdit(old_name)
        input_price = QLineEdit(old_price)

        form_layout.addRow("Nama Produk:", input_name)
        form_layout.addRow("Harga:", input_price)

        btn_update = QPushButton("Simpan Perubahan")
        btn_cancel = QPushButton("Batal")

        btn_update.clicked.connect(lambda: self.update_product(dialog, product_id, input_name.text(), input_price.text()))
        btn_cancel.clicked.connect(dialog.reject)

        form_layout.addRow(btn_update, btn_cancel)

        dialog.exec()

    def update_product(self, dialog, product_id, name, price):
        """Update data produk ke database"""
        if not name or not price:
            QMessageBox.warning(self, "Error", "Nama dan harga tidak boleh kosong!")
            return

        try:
            price = float(price)
        except ValueError:
            QMessageBox.warning(self, "Error", "Harga harus berupa angka!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET name = ?, price = ? WHERE id = ?", (name, price, product_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Sukses", f"Produk '{name}' berhasil diperbarui.")
        dialog.accept()
        self.load_products()

    # ==========================================
    # HAPUS PRODUK
    # ==========================================
    def delete_product(self):
        """Hapus produk yang dipilih dari database"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Pilih produk yang ingin dihapus terlebih dahulu.")
            return

        product_id = self.table.item(selected_row, 0).text()
        product_name = self.table.item(selected_row, 1).text()

        # Konfirmasi hapus
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
        self.main_window.show_menu()
