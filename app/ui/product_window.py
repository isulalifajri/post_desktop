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
        self.product_ids = []  # menyimpan id asli dari database

        # Layout utama
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Judul
        title = QLabel("🧾 Daftar Produk")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #2C3E50;
            margin-bottom: 10px;
            text-align: center;
        """)
        layout.addWidget(title)

        # ==========================================
        # Tombol Export (di atas pencarian)
        # ==========================================
        export_layout = QHBoxLayout()
        export_layout.addStretch()  # supaya tombol rata kanan

        btn_export_csv = QPushButton("📄 Export CSV")
        btn_export_csv.setStyleSheet("""
            background-color: #f39c12;
            color: white;
            padding: 8px 14px;
            font-weight: bold;
            border-radius: 6px;
        """)
        btn_export_csv.clicked.connect(self.export_to_csv)

        btn_export_pdf = QPushButton("🧾 Export PDF")
        btn_export_pdf.setStyleSheet("""
            background-color: #8e44ad;
            color: white;
            padding: 8px 14px;
            font-weight: bold;
            border-radius: 6px;
        """)
        btn_export_pdf.clicked.connect(self.export_to_pdf)

        export_layout.addWidget(btn_export_csv)
        export_layout.addWidget(btn_export_pdf)
        layout.addLayout(export_layout)

        # Pencarian Produk Real-time
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari produk berdasarkan nama...")
        self.search_input.setStyleSheet("padding: 8px; font-size: 16px;")
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        self.search_input.textChanged.connect(self.search_product)

        # Tabel Produk
        self.table = QTableWidget()
        self.table.setColumnCount(5)
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
            QTableWidget::item:selected {
                background-color: #2980b9;
                color: white;
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
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        # Tombol tambah & kembali
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

        self.product_ids = []
        self.table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            product_id, name, price, stock = row
            self.product_ids.append(product_id)

            self.table.setRowHeight(i, 50)

            # No urut manual
            no_item = QTableWidgetItem(str(i + 1))
            no_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, no_item)

            # Nama
            item_name = QTableWidgetItem(name)
            item_name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 1, item_name)

            # Harga
            price_str = f"Rp {int(price):,}".replace(",", ".")
            item_price = QTableWidgetItem(price_str)
            item_price.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 2, item_price)

            # Stok
            item_stock = QTableWidgetItem(str(stock))
            item_stock.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 3, item_stock)

            # Aksi
            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("background-color: #2980b9; color: white; padding: 8px 16px; font-weight: bold; font-size: 14px;")
            btn_edit.clicked.connect(lambda checked, r=i: self.open_edit_product(r))

            btn_delete = QPushButton("Hapus")
            btn_delete.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px 16px; font-weight: bold; font-size: 14px;")
            btn_delete.clicked.connect(lambda checked, r=i: self.delete_product(r))

            action_layout = QHBoxLayout()
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)
            action_layout.setContentsMargins(0,0,0,0)
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
            item = self.table.item(i, 1)  # Nama Produk
            self.table.setRowHidden(i, query not in item.text().lower())

    # ==========================================
    # TAMBAH PRODUK
    # ==========================================
    def open_add_product(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Tambah Produk")
        dialog.setFixedWidth(400)
        dialog.setStyleSheet("background-color: #fdfdfd; border-radius: 5px;")

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.setSpacing(10)

        # Input fields dengan style modern
        input_name = QLineEdit()
        input_name.setPlaceholderText("Input your name product")
        input_name.setStyleSheet("padding: 5px; font-size: 16px; border: 1px solid #bdc3c7; border-radius: 6px;")

        input_price = QLineEdit()
        input_price.setPlaceholderText("exc: 12000")
        input_price.setStyleSheet("padding: 5px; font-size: 16px; border: 1px solid #bdc3c7; border-radius: 6px;")

        input_stock = QLineEdit()
        input_stock.setPlaceholderText("exc: 10")
        input_stock.setStyleSheet("padding: 5px; font-size: 16px; border: 1px solid #bdc3c7; border-radius: 6px;")

        label_name = QLabel("Nama Produk:")
        label_name.setStyleSheet("font-weight: bold; font-size: 16px;")
        form_layout.addRow(label_name, input_name)

        label_price = QLabel("Harga:")
        label_price.setStyleSheet("font-weight: bold; font-size: 16px;")
        form_layout.addRow(label_price, input_price)

        label_stock = QLabel("Stok:")
        label_stock.setStyleSheet("font-weight: bold; font-size: 16px;")
        form_layout.addRow(label_stock, input_stock)

        # Tombol simpan dan batal dengan style modern
        btn_save = QPushButton("Simpan")
        btn_save.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #27ae60, stop:1 #2ecc71);
            color: white;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 5px;
        """)
        btn_save.clicked.connect(lambda: self.save_product(dialog, input_name.text(), input_price.text(), input_stock.text()))

        btn_cancel = QPushButton("Batal")
        btn_cancel.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 5px;
        """)
        btn_cancel.clicked.connect(dialog.reject)

        # Layout tombol
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(btn_save)
        button_layout.addWidget(btn_cancel)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        dialog.setLayout(main_layout)

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

        msg = QMessageBox(self)
        msg.setWindowTitle("✅ Sukses")
        msg.setText(f"Produk <b>{name}</b> berhasil ditambahkan!")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f9f9f9;
                border-radius: 10px;
                padding: 15px;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 16px;
                font-weight: bold;
            }
            QMessageBox QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        msg.exec()

        dialog.accept()
        self.load_products()

    # ==========================================
    # EDIT PRODUK
    # ==========================================
    def open_edit_product(self, row_index):
        product_id = self.product_ids[row_index]
        old_name = self.table.item(row_index, 1).text()
        old_price = self.table.item(row_index, 2).text()
        old_stock = self.table.item(row_index, 3).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Produk")
        dialog.setFixedWidth(400)
        dialog.setStyleSheet("background-color: #fdfdfd; border-radius: 10px;")

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.setSpacing(15)

        input_name = QLineEdit(old_name)
        input_name.setStyleSheet("padding: 8px; font-size: 16px; border: 1px solid #bdc3c7; border-radius: 6px;")

        old_price_clean = old_price.replace("Rp ", "").replace(".", "").strip()
        input_price = QLineEdit(old_price_clean)
        input_price.setStyleSheet("padding: 8px; font-size: 16px; border: 1px solid #bdc3c7; border-radius: 6px;")

        input_stock = QLineEdit(old_stock)
        input_stock.setStyleSheet("padding: 8px; font-size: 16px; border: 1px solid #bdc3c7; border-radius: 6px;")

        label_name = QLabel("Nama Produk:")
        label_name.setStyleSheet("font-weight: bold; font-size: 16px;")
        form_layout.addRow(label_name, input_name)

        label_price = QLabel("Harga:")
        label_price.setStyleSheet("font-weight: bold; font-size: 16px;")
        form_layout.addRow(label_price, input_price)

        label_stock = QLabel("Stok:")
        label_stock.setStyleSheet("font-weight: bold; font-size: 16px;")
        form_layout.addRow(label_stock, input_stock)

        btn_update = QPushButton("💾 Simpan Perubahan")
        btn_update.setStyleSheet("""
            background-color: #2980b9;
            color: white;
            padding: 8px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 8px;
        """)
        btn_update.clicked.connect(lambda: self.update_product(dialog, product_id, input_name.text(), input_price.text(), input_stock.text()))

        btn_cancel = QPushButton("❌ Batal")
        btn_cancel.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            padding: 8px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 8px;
        """)
        btn_cancel.clicked.connect(dialog.reject)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(btn_update)
        button_layout.addWidget(btn_cancel)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        dialog.setLayout(main_layout)

        dialog.exec()


    def update_product(self, dialog, product_id, name, price, stock):
        if not name or not price:
            QMessageBox.warning(self, "Error", "Nama dan harga tidak boleh kosong!")
            return
        try:
            price = float(price.replace("Rp", "").replace(".", "").strip())
            stock = int(stock)
        except ValueError:
            QMessageBox.warning(self, "Error", "Harga dan stok harus berupa angka!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET name=?, price=?, stock=? WHERE id=?", (name, price, stock, product_id))
        conn.commit()
        conn.close()

        msg = QMessageBox(self)
        msg.setWindowTitle("✅ Sukses")
        msg.setText(f"Produk <b>{name}</b> berhasil diperbarui!")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f9f9f9;
                border-radius: 10px;
                padding: 15px;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 16px;
                font-weight: bold;
            }
            QMessageBox QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        msg.exec()

        dialog.accept()
        self.load_products()


    # ==========================================
    # HAPUS PRODUK
    # ==========================================
    def delete_product(self, row_index):
        product_id = self.product_ids[row_index]
        product_name = self.table.item(row_index, 1).text()

        # === Konfirmasi hapus dengan style modern ===
        confirm_box = QMessageBox(self)
        confirm_box.setWindowTitle("⚠️ Konfirmasi Hapus")
        confirm_box.setText(f"Yakin ingin menghapus produk <b>{product_name}</b>?")
        confirm_box.setIcon(QMessageBox.Icon.Warning)
        confirm_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        confirm_box.setDefaultButton(QMessageBox.StandardButton.No)

        confirm_box.setStyleSheet("""
            QMessageBox {
                background-color: #fefefe;
                border-radius: 10px;
                padding: 15px;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 16px;
                font-weight: bold;
            }
            QMessageBox QPushButton {
                background-color: #c0392b;
                color: white;
                font-weight: bold;
                padding: 8px 18px;
                border-radius: 6px;
                min-width: 80px;
            }
            QMessageBox QPushButton[text="&Yes"] {
                background-color: #27ae60;
            }
            QMessageBox QPushButton[text="&Yes"]:hover {
                background-color: #2ecc71;
            }
            QMessageBox QPushButton:hover {
                background-color: #e74c3c;
            }
            QMessageBox QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)

        confirm = confirm_box.exec()

        # === Jika user klik "Ya" ===
        if confirm == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
            conn.commit()
            conn.close()

            # === Pesan sukses dengan style sama ===
            success_box = QMessageBox(self)
            success_box.setWindowTitle("✅ Sukses")
            success_box.setText(f"Produk <b>{product_name}</b> telah dihapus.")
            success_box.setIcon(QMessageBox.Icon.Information)
            success_box.setStyleSheet("""
                QMessageBox {
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 15px;
                }
                QMessageBox QLabel {
                    color: #2c3e50;
                    font-size: 16px;
                    font-weight: bold;
                }
                QMessageBox QPushButton {
                    background-color: #27ae60;
                    color: white;
                    font-weight: bold;
                    padding: 8px 16px;
                    border-radius: 6px;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #2ecc71;
                }
            """)
            success_box.exec()

            self.load_products()

    # ==========================================
    # EXPORT TO CSV DENGAN TANGGAL HARI INI
    # ==========================================
    def export_to_csv(self):
        import csv
        from datetime import datetime
        from PyQt6.QtWidgets import QFileDialog, QMessageBox

        # Ambil tanggal hari ini
        today_str = datetime.now().strftime("%Y-%m-%d")
        default_filename = f"daftar_product_{today_str}.csv"

        # Pilih lokasi file (dengan nama default)
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Simpan CSV", default_filename, "CSV Files (*.csv)"
        )
        if not file_path:
            return

        # Ambil data dari database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, price, stock FROM products")
        rows = cursor.fetchall()
        conn.close()

        # Simpan ke CSV
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Nama Produk", "Harga (Rp)", "Stok"])
                for name, price, stock in rows:
                    price_str = f"{int(price):,}".replace(",", ".")  # format Indonesia
                    writer.writerow([name, price_str, stock])

            QMessageBox.information(self, "Sukses", f"Data produk berhasil diexport ke:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal export CSV:\n{str(e)}")


    # ==========================================
    # EXPORT TO PDF
    # ==========================================
        # ==========================================
    # EXPORT TO PDF DENGAN NAMA FILE & WAKTU CETAK
    # ==========================================
    def export_to_pdf(self):
        from fpdf import FPDF
        from datetime import datetime
        from PyQt6.QtWidgets import QFileDialog, QMessageBox

        # Ambil tanggal & waktu sekarang
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        default_filename = f"daftar_product_{today_str}.pdf"

        # Pilih lokasi file dengan nama default
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Simpan PDF", default_filename, "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        # Ambil data dari database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, price, stock FROM products")
        rows = cursor.fetchall()
        conn.close()

        # Buat file PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Daftar Produk", ln=True, align="C")
        pdf.ln(5)

        # Tambahkan waktu cetak di bawah judul
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, f"Dicetak pada: {today_str} pukul {time_str}", ln=True, align="C")
        pdf.ln(8)

        # Header tabel
        pdf.set_font("Arial", "B", 12)
        pdf.cell(80, 10, "Nama Produk", 1, align="C")
        pdf.cell(40, 10, "Harga", 1, align="C")
        pdf.cell(30, 10, "Stok", 1, align="C")
        pdf.ln()

        # Isi tabel
        pdf.set_font("Arial", "", 12)
        for name, price, stock in rows:
            pdf.cell(80, 10, name, 1)
            pdf.cell(40, 10, f"Rp {int(price):,}".replace(",", "."), 1, align="R")
            pdf.cell(30, 10, str(stock), 1, align="C")
            pdf.ln()

        # Simpan PDF
        pdf.output(file_path)

        QMessageBox.information(self, "Sukses", f"Data produk berhasil diexport ke:\n{file_path}")



    # ==========================================
    # KEMBALI KE MENU UTAMA
    # ==========================================
    def go_back(self):
        self.main_window.show_dashboard()
