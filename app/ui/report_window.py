from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QDateEdit
)
from PyQt6.QtCore import QDate
from app.database.db import get_connection
import csv
from PyQt6.QtWidgets import QFileDialog, QMessageBox



class ReportWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        title = QLabel("📊 Laporan Penjualan")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Filter tanggal
        layout.addWidget(QLabel("Pilih Tanggal:"))
        self.date_picker = QDateEdit()
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setCalendarPopup(True)
        layout.addWidget(self.date_picker)

        # Tombol
        btn_load = QPushButton("Tampilkan Laporan")
        btn_export = QPushButton("Export ke CSV")
        btn_back = QPushButton("⬅️ Kembali ke Menu")

        btn_load.clicked.connect(self.load_report)
        btn_export.clicked.connect(self.export_csv)
        btn_back.clicked.connect(self.go_back)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_load)
        hbox.addWidget(btn_export)
        hbox.addWidget(btn_back)
        layout.addLayout(hbox)

        # Tabel laporan
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Produk", "Harga", "Jumlah", "Total"])
        layout.addWidget(self.table)

        # Total penjualan
        self.total_label = QLabel("Total Penjualan: Rp0")
        self.total_label.setStyleSheet("font-weight: bold; margin-top: 10px; font-size: 14px;")
        layout.addWidget(self.total_label)

        self.setLayout(layout)

    def load_report(self):
        """Ambil data penjualan berdasarkan tanggal"""
        selected_date = self.date_picker.date().toString("yyyy-MM-dd")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, p.name, p.price, s.quantity, s.total
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE DATE(s.sale_date) = ?
        """, (selected_date,))
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        total_sales = 0

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))
            total_sales += row[4]

        self.total_label.setText(f"Total Penjualan: Rp{total_sales:,.0f}")

    def export_csv(self):
        """Ekspor laporan ke file CSV"""
        selected_date = self.date_picker.date().toString("yyyy-MM-dd")
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Laporan Penjualan",
            f"laporan_{selected_date}.csv",
            "CSV Files (*.csv)"
        )

        if not filename:
            return  # user batal memilih file

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, p.name, p.price, s.quantity, s.total
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE DATE(s.sale_date) = ?
        """, (selected_date,))
        rows = cursor.fetchall()
        conn.close()

        # Tulis ke file CSV
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Produk", "Harga", "Jumlah", "Total"])
            for row in rows:
                writer.writerow(row)

        QMessageBox.information(self, "Berhasil", f"Laporan disimpan ke:\n{filename}")


    def go_back(self):
        self.main_window.show_menu()
