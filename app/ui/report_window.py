from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QComboBox, QFileDialog, QMessageBox, QHeaderView
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

        # ================== Filter bulan & tahun ==================
        label = QLabel("Pilih Bulan & Tahun:")
        label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
        """)
        layout.addWidget(label)

        # ComboBox
        self.cmb_month = QComboBox()
        self.cmb_year = QComboBox()

        combo_style = """
            QComboBox {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 8px;
            }
        """
        self.cmb_month.setStyleSheet(combo_style)
        self.cmb_year.setStyleSheet(combo_style)

        months = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        self.cmb_month.addItems(months)

        current_year = datetime.now().year
        for y in range(current_year - 4, current_year + 1):
            self.cmb_year.addItem(str(y))

        self.cmb_month.setCurrentIndex(datetime.now().month - 1)
        self.cmb_year.setCurrentText(str(current_year))

        # Layout filter
        hbox_filter = QHBoxLayout()
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

        # Styling tombol
        btn_style = {
            "load": {"bg": "#3498db", "hover": "#2980b9", "pressed": "#1d4ed8"},
            "export": {"bg": "#27ae60", "hover": "#2ecc71", "pressed": "#27ae60"},
            "back": {"bg": "#e74c3c", "hover": "#c0392b", "pressed": "#e74c3c"}
        }

        def set_button_style(btn, style):
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {style['bg']};
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                    min-width: 160px;
                }}
                QPushButton:hover {{
                    background-color: {style['hover']};
                }}
                QPushButton:pressed {{
                    background-color: {style['pressed']};
                }}
            """)

        set_button_style(btn_load, btn_style["load"])
        set_button_style(btn_export, btn_style["export"])
        set_button_style(btn_back, btn_style["back"])

        hbox_btn = QHBoxLayout()
        hbox_btn.addWidget(btn_load)
        hbox_btn.addWidget(btn_export)
        hbox_btn.addWidget(btn_back)
        layout.addLayout(hbox_btn)

        # ================== Tabel laporan ==================
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Tanggal Pembelian", "Produk", "Harga", "Jumlah", "Subtotal"])
        self.table.verticalHeader().setVisible(False)
        self.table.setWordWrap(True)
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
                white-space: pre-wrap;
            }
            QTableWidget::item:selected {
                background-color: #f39c12;
                color: white;
            }
        """)
        layout.addWidget(self.table)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # Label total
        self.total_label = QLabel("Total Penjualan: Rp0 | Total Barang Terjual: 0")
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

    # ======================= UTIL: Format tanggal Indonesia =======================
    def format_tanggal(self, tanggal_str):
        bulan_indonesia = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        try:
            dt = datetime.strptime(tanggal_str, "%Y-%m-%d %H:%M:%S")
            return f"{dt.day} {bulan_indonesia[dt.month - 1]} {dt.year} {dt.strftime('%H:%M')}"
        except ValueError:
            try:
                dt = datetime.strptime(tanggal_str, "%Y-%m-%d")
                return f"{dt.day} {bulan_indonesia[dt.month - 1]} {dt.year}"
            except ValueError:
                return tanggal_str  # fallback

    # ======================= UTIL: Format Rupiah =======================
    def format_rupiah(self, amount):
        """Format angka menjadi Rp 12.000 tanpa desimal"""
        return f"Rp {int(amount):,}".replace(",", ".")

    # ======================= LOAD REPORT =======================
    def load_report(self):
        month_index = self.cmb_month.currentIndex() + 1
        year = int(self.cmb_year.currentText())

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.sale_date, p.name, si.price, si.qty, (si.price * si.qty) AS subtotal
            FROM sales s
            JOIN sales_items si ON s.id = si.sale_id
            JOIN products p ON si.product_id = p.id
            WHERE strftime('%Y', s.sale_date) = ? AND strftime('%m', s.sale_date) = ?
            ORDER BY s.sale_date ASC
        """, (str(year), f"{month_index:02d}"))
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        self.empty_label.setText("")
        total_sales = 0
        total_qty = 0

        if not rows:
            self.empty_label.setText("📭 Belum ada transaksi pada bulan ini.")
            self.total_label.setText("Total Penjualan: Rp0 | Total Barang Terjual: 0")
            return

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            formatted_date = self.format_tanggal(row[0])
            row_data = [
                formatted_date,
                row[1],
                self.format_rupiah(row[2]),  # Harga
                row[3],
                self.format_rupiah(row[4])   # Subtotal
            ]

            for j, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(1)  # kiri-atas
                self.table.setItem(i, j, item)

            total_sales += row[4]
            total_qty += row[3]

        self.table.resizeRowsToContents()
        self.total_label.setText(f"Total Penjualan: {self.format_rupiah(total_sales)} | Total Barang Terjual: {total_qty}")

    # ======================= EXPORT CSV =======================
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
            SELECT s.sale_date, p.name, si.price, si.qty, (si.price * si.qty) AS subtotal
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

        total_qty = 0
        total_sales = 0
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Tanggal Pembelian", "Produk", "Harga", "Jumlah", "Subtotal"])
            for row in rows:
                formatted_date = self.format_tanggal(row[0])
                row_data = [
                    formatted_date,
                    row[1],
                    self.format_rupiah(row[2]),
                    row[3],
                    self.format_rupiah(row[4])
                ]
                writer.writerow(row_data)
                total_sales += row[4]
                total_qty += row[3]

            writer.writerow([])
            writer.writerow(["", "TOTAL", "", total_qty, self.format_rupiah(total_sales)])

        QMessageBox.information(self, "Berhasil", f"Laporan disimpan ke:\n{filename}")

    # ======================= KEMBALI KE MENU =======================
    def go_back(self):
        self.main_window.show_dashboard()
