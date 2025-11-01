from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QComboBox, QFileDialog, QMessageBox, QHeaderView
)
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QCategoryAxis
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QPointF
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
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(label)

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

        def style_btn(btn, color):
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                    min-width: 160px;
                }}
                QPushButton:hover {{
                    background-color: #2c3e50;
                }}
            """)

        style_btn(btn_load, "#3498db")
        style_btn(btn_export, "#27ae60")
        style_btn(btn_back, "#e74c3c")

        hbox_btn = QHBoxLayout()
        hbox_btn.addWidget(btn_load)
        hbox_btn.addWidget(btn_export)
        hbox_btn.addWidget(btn_back)
        layout.addLayout(hbox_btn)

        # ================== Layout utama tabel + grafik ==================
        hbox_main = QHBoxLayout()

        # ===== TABEL LAPORAN =====
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
        self.table.setColumnWidth(0, 180)
        self.table.horizontalHeader().setStretchLastSection(True)
        hbox_main.addWidget(self.table, 3)

        # ===== GRAFIK (Line Chart) =====
        self.chart = QChart()
        self.chart.setTitle("📈 Tren Barang Terjual per Tanggal")
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.setBackgroundBrush(QColor("#f8f9fa"))

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        hbox_main.addWidget(self.chart_view, 2)  # Lebar relatif lebih kecil dari tabel

        layout.addLayout(hbox_main)

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
        self.empty_label.setStyleSheet("color: gray; font-style: italic; margin-top: 5px;")
        layout.addWidget(self.empty_label)

        self.setLayout(layout)
        self.load_report()

    # ======== Format tanggal Indonesia ========
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
                return tanggal_str

    # ======== Load Report + Grafik ========
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
            self.chart.removeAllSeries()
            return

        self.table.setRowCount(len(rows))
        sales_per_day = {}

        for i, row in enumerate(rows):
            formatted_date = self.format_tanggal(row[0])
            row_data = [formatted_date, row[1], row[2], row[3], row[4]]
            for j, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(i, j, item)

            total_sales += row[4]
            total_qty += row[3]

            # Rekap jumlah per tanggal
            tanggal_asli = row[0].split(" ")[0]
            sales_per_day[tanggal_asli] = sales_per_day.get(tanggal_asli, 0) + row[3]

        self.table.resizeRowsToContents()
        self.total_label.setText(f"Total Penjualan: Rp{total_sales:,.0f} | Total Barang Terjual: {total_qty}")

        # ===== Update grafik =====
        self.update_chart(sales_per_day)

    def update_chart(self, data_harian):
        self.chart.removeAllSeries()
        if not data_harian:
            return

        # Buat series garis
        series = QLineSeries()
        sorted_days = sorted(data_harian.keys())
        for idx, tgl in enumerate(sorted_days):
            series.append(QPointF(idx + 1, data_harian[tgl]))

        series.setColor(QColor("#3498db"))
        series.setName("Barang Terjual")
        self.chart.addSeries(series)

        # Buat sumbu X (tanggal)
        axis_x = QCategoryAxis()
        for idx, tgl in enumerate(sorted_days):
            try:
                dt = datetime.strptime(tgl, "%Y-%m-%d")
                label = str(dt.day)
            except ValueError:
                label = tgl
            axis_x.append(label, idx + 1)
        axis_x.setLabelsAngle(-45)
        axis_x.setTitleText("Tanggal")
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        # Buat sumbu Y (jumlah)
        axis_y = QValueAxis()
        axis_y.setTitleText("Jumlah Barang Terjual")
        axis_y.setLabelFormat("%d")
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

    # ======== Export CSV ========
    def export_csv(self):
        month_index = self.cmb_month.currentIndex() + 1
        year = int(self.cmb_year.currentText())
        month_name = self.cmb_month.currentText()

        filename, _ = QFileDialog.getSaveFileName(
            self, "Simpan Laporan Penjualan",
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
            QMessageBox.information(self, "Tidak Ada Data", "Tidak ada transaksi untuk bulan ini.")
            return

        total_qty = 0
        total_sales = 0
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Tanggal Pembelian", "Produk", "Harga", "Jumlah", "Subtotal"])
            for row in rows:
                formatted_date = self.format_tanggal(row[0])
                row_data = [formatted_date, row[1], row[2], row[3], row[4]]
                writer.writerow(row_data)
                total_sales += row[4]
                total_qty += row[3]

            writer.writerow([])
            writer.writerow(["", "TOTAL", "", total_qty, total_sales])

        QMessageBox.information(self, "Berhasil", f"Laporan disimpan ke:\n{filename}")

    def go_back(self):
        self.main_window.show_dashboard()
