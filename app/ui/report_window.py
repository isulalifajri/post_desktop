from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QComboBox, QFileDialog, QMessageBox
)
from app.database.db import get_connection
import csv
from datetime import datetime

class ReportWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        # Judul
        title = QLabel("📊 Laporan Penjualan Bulanan")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #2C3E50;
            margin-bottom: 20px;
            text-align: center;
        """)
        layout.addWidget(title)

        # Filter bulan & tahun
        layout.addWidget(QLabel("Pilih Bulan & Tahun:"))

        hbox_filter = QHBoxLayout()
        self.cmb_month = QComboBox()
        self.cmb_year = QComboBox()

        months = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        self.cmb_month.addItems(months)

        current_year = datetime.now().year
        for y in range(current_year - 4, current_year + 1):
            self.cmb_year.addItem(str(y))

        current_month = datetime.now().month
        self.cmb_month.setCurrentIndex(current_month - 1)
        self.cmb_year.setCurrentText(str(current_year))

        hbox_filter.addWidget(self.cmb_month)
        hbox_filter.addWidget(self.cmb_year)
        layout.addLayout(hbox_filter)

        # Tombol
        btn_load = QPushButton("Tampilkan Laporan")
        btn_export = QPushButton("Export ke CSV")
        btn_back = QPushButton("⬅️ Kembali ke Menu")

        btn_load.clicked.connect(self.load_report)
        btn_export.clicked.connect(self.export_csv)
        btn_back.clicked.connect(self.go_back)

        # Styling Tombol
        btn_load.setStyleSheet("""
            background-color: #3498db;
            color: white;
            font-size: 14px;
            padding: 10px;
            border-radius: 5px;
            min-width: 160px;
        """)
        btn_export.setStyleSheet("""
            background-color: #27ae60;
            color: white;
            font-size: 14px;
            padding: 10px;
            border-radius: 5px;
            min-width: 160px;
        """)
        btn_back.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            font-size: 14px;
            padding: 10px;
            border-radius: 5px;
            min-width: 160px;
        """)

        # Hover effect for buttons
        btn_load.setStyleSheet(btn_load.styleSheet() + """
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_export.setStyleSheet(btn_export.styleSheet() + """
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        btn_back.setStyleSheet(btn_back.styleSheet() + """
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

        # Layout Tombol
        hbox_btn = QHBoxLayout()
        hbox_btn.addWidget(btn_load)
        hbox_btn.addWidget(btn_export)
        hbox_btn.addWidget(btn_back)
        layout.addLayout(hbox_btn)

        # Tabel laporan
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Hanya 4 kolom setelah menghapus ID transaksi
        self.table.setHorizontalHeaderLabels(["Produk", "Harga", "Jumlah", "Subtotal"])
        
        # Hapus header vertikal (nomor urut)
        self.table.verticalHeader().setVisible(False)  # Menyembunyikan header vertikal

        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                font-size: 14px;
            }
            QTableWidget QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #f39c12;
                color: white;
            }
        """)
        layout.addWidget(self.table)

        # Label total penjualan
        self.total_label = QLabel("Total Penjualan: Rp0")
        self.total_label.setStyleSheet("""
            font-weight: bold;
            font-size: 16px;
            margin-top: 10px;
            color: #16a085;
        """)
        layout.addWidget(self.total_label)

        # Label pesan kosong
        self.empty_label = QLabel("")
        self.empty_label.setStyleSheet("""
            color: gray;
            font-style: italic;
            margin-top: 5px;
        """)
        layout.addWidget(self.empty_label)

        self.setLayout(layout)

        # Tampilkan laporan default bulan ini
        self.load_report()

    def load_report(self):
        month_index = self.cmb_month.currentIndex() + 1
        year = int(self.cmb_year.currentText())

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, p.name, si.price, si.qty, (si.price * si.qty) AS subtotal
            FROM sales s
            JOIN sales_items si ON s.id = si.sale_id
            JOIN products p ON si.product_id = p.id
            WHERE strftime('%Y', s.sale_date) = ? AND strftime('%m', s.sale_date) = ?
            ORDER BY s.sale_date ASC
        """, (str(year), f"{month_index:02d}"))
        rows = cursor.fetchall()
        conn.close()

        # Bersihkan tabel dan label dulu
        self.table.setRowCount(0)
        self.empty_label.setText("")
        total_sales = 0

        if not rows:
            # Jika tidak ada data
            self.empty_label.setText("📭 Belum ada transaksi pada bulan ini.")
            self.total_label.setText("Total Penjualan: Rp0")
            return

        # Jika ada data, isi tabel
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row[1:]):  # Mengambil mulai dari indeks ke-1 (produk)
                self.table.setItem(i, j, QTableWidgetItem(str(value)))
            total_sales += row[4]

        self.total_label.setText(f"Total Penjualan: Rp{total_sales:,.0f}")

    def export_csv(self):
        month_index = self.cmb_month.currentIndex() + 1
        year = int(self.cmb_year.currentText())
        month_name = self.cmb_month.currentText()

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Laporan Penjualan",
            f"laporan_{month_name}_{year}.csv",
            "CSV Files (*.csv)"
        )

        if not filename:
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, p.name, si.price, si.qty, (si.price * si.qty) AS subtotal
            FROM sales s
            JOIN sales_items si ON s.id = si.sale_id
            JOIN products p ON si.product_id = p.id
            WHERE strftime('%Y', s.sale_date) = ? AND strftime('%m', s.sale_date) = ?
            ORDER BY s.sale_date ASC
        """, (str(year), f"{month_index:02d}"))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            QMessageBox.information(self, "Tidak Ada Data", "Tidak ada transaksi untuk bulan ini, jadi tidak bisa diekspor.")
            return

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Produk", "Harga", "Jumlah", "Subtotal"])  # Header CSV tanpa ID
            for row in rows:
                writer.writerow(row[1:])  # Menulis data tanpa ID

        QMessageBox.information(self, "Berhasil", f"Laporan disimpan ke:\n{filename}")

    def go_back(self):
        self.main_window.show_dashboard()
