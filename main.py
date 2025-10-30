# main.py
import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout

# 1. Buat aplikasi utama
app = QApplication(sys.argv)

# 2. Buat jendela (window)
window = QWidget()
window.setWindowTitle("POS Desktop - Test")
window.setGeometry(300, 200, 400, 200)

# 3. Tambahkan teks sederhana
layout = QVBoxLayout()
label = QLabel("Hello, POS Desktop pertama kamu!")
layout.addWidget(label)
window.setLayout(layout)

# 4. Tampilkan jendela
window.show()

# 5. Jalankan event loop
sys.exit(app.exec())
