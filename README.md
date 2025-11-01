## Membuat aplikasi pos desktop dg python

mkdir pos_desktop
cd pos_desktop

jalankan perintah ini: 

```
python -m venv venv
# Activate venv:
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# window git bash
source venv/Scripts/activate
```
lanjut didalam venv((venv) PS D:\PYTHON\post_desktop>) -> muncul setelah venv diaktfikan:

```
python -m pip install --upgrade pip setuptools wheel
pip install pyqt6
```

untuk percobaan buat file `main.py`, isi seperti ini:
```
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

```

kemudian jalankan perintah: `python main.py`
jika muncul jendela window(GUI) berarti berhasil

# Menu

Dashboard
├── Produk
├── Transaksi
├── Laporan
└── Pengaturan

# untuk menampilkan data dlm bentuk chart

```
pip install matplotlib

```

# untuk menampilkan data kedalam bentuk pdf

```
pip install reportlab

```




