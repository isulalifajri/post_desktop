# --- app/database/db.py ---

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).resolve().parent.parent.parent / "pos.db"


# ------------------------------
# CONNECT & INIT DATABASE
# ------------------------------
def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Tabel produk
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
    )
    """)

    # Tabel penjualan
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_date TEXT NOT NULL,
        total REAL NOT NULL
    )
    """)

    # Tabel detail item penjualan
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        qty INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY(sale_id) REFERENCES sales(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)

    conn.commit()
    conn.close()


# ------------------------------
# SIMPLE GETTER
# ------------------------------
def get_all_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock FROM products ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "price": r[2], "stock": r[3]} for r in rows]

# =====================================================
# 📈 Statistik untuk Dashboard
# =====================================================
def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor()

    # Jumlah produk
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # Transaksi hari ini
    cursor.execute("""
        SELECT COUNT(*)
        FROM sales
        WHERE DATE(sale_date) = DATE('now', 'localtime')
    """)
    sales_today = cursor.fetchone()[0]

    # Total pendapatan hari ini
    cursor.execute("""
        SELECT IFNULL(SUM(si.qty * si.price), 0)
        FROM sales s
        JOIN sales_items si ON s.id = si.sale_id
        WHERE DATE(s.sale_date) = DATE('now', 'localtime')
    """)
    revenue_today = cursor.fetchone()[0]

    conn.close()
    return {
        "products": total_products,
        "sales_today": sales_today,
        "revenue_today": revenue_today
    }


# =====================================================
# 📊 Pendapatan 3 Bulan Terakhir
# =====================================================
def get_last_3_months_revenue():
    from datetime import datetime, timedelta
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            strftime('%Y-%m', s.sale_date) AS month,
            SUM(si.qty * si.price) AS total
        FROM sales s
        JOIN sales_items si ON s.id = si.sale_id
        WHERE s.sale_date >= DATE('now', '-3 months')
        GROUP BY month
        ORDER BY month
    """)
    data = cursor.fetchall()
    conn.close()

    # ubah hasil DB ke dict: {'2025-08': 50000, '2025-10': 120000, ...}
    data_dict = {month: (total or 0) for month, total in data}

    # buat list 3 bulan terakhir sesuai format DB
    months = []
    today = datetime.now().replace(day=1)
    for i in range(2, -1, -1):
        m = (today - timedelta(days=30 * i)).strftime("%Y-%m")
        months.append(m)

    # isi pendapatan, kalau bulan hilang = 0
    formatted = [(m, data_dict.get(m, 0)) for m in months]

    return formatted
