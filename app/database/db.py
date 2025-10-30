import sqlite3
from pathlib import Path

# Tentukan lokasi database (file pos.db akan dibuat di root project)
DB_PATH = Path(__file__).resolve().parent.parent.parent / "pos.db"

def get_connection():
    """Membuat koneksi ke database SQLite"""
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    """Inisialisasi tabel-tabel awal jika belum ada"""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabel barang (products)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0
    )
    """)

    # Tabel transaksi (sales)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total REAL NOT NULL,
        sale_date TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    """)

    conn.commit()
    conn.close()
