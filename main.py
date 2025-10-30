from PyQt6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.database.db import init_db
import sys

if __name__ == "__main__":
    init_db()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
