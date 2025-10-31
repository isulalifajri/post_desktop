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

        title = QLabel("📊 Laporan Penjualan Bulanan")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # ===============================
        # Filter bulan & tahun
        # ===============================
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

        # ===============================
        # Tombol
        # ===============================
        btn_load = QPushButton("Tampilkan Laporan")
        btn_export = QPushButton("Export ke CSV")
        btn_back = QPushButton("⬅️ Kembali ke Menu")

        btn_load.clicked.connect(self.load_report)
        btn_export.clicked.connect(self.export_csv)
        btn_back.clicked.connect(self.go_back)

        hbox_btn = QHBoxLayout()
        hbox_btn.addWidget(btn_load)
        hbox_btn.addWidget(btn_export)
        hbox_btn.addWidget(btn_back)
        layout.addLayout(hbox_btn)

        # ===============================
        # Tabel laporan
        # ===============================
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID Transaksi", "Produk", "Harga", "Jumlah", "Subtotal"])
        layout.addWidget(self.table)

        # Label total
        self.total_label = QLabel("Total Penjualan: Rp0")
        self.total_label.setStyleSheet("font-weight: bold; margin-top: 10px; font-size: 14px;")
        layout.addWidget(self.total_label)

        # Label pesan kosong (jika tidak ada data)
        self.empty_label = QLabel("")
        self.empty_label.setStyleSheet("color: gray; font-style: italic; margin-top: 5px;")
        layout.addWidget(self.empty_label)

        self.setLayout(layout)

        # Tampilkan laporan default bulan ini
        self.load_report()

    # ==================================================
    # FUNGSI UTAMA: LOAD LAPORAN PER BULAN
    # ==================================================
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
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))
            total_sales += row[4]

        self.total_label.setText(f"Total Penjualan: Rp{total_sales:,.0f}")

    # ==================================================
    # EXPORT CSV
    # ==================================================
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
            writer.writerow(["ID Transaksi", "Produk", "Harga", "Jumlah", "Subtotal"])
            for row in rows:
                writer.writerow(row)

        QMessageBox.information(self, "Berhasil", f"Laporan disimpan ke:\n{filename}")

    # ==================================================
    # KEMBALI KE DASHBOARD
    # ==================================================
    def go_back(self):
        self.main_window.show_dashboard()
