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
# DASHBOARD STATS
# ------------------------------
def get_dashboard_stats():
    conn = get_connection()
    cur = conn.cursor()

    # Jumlah produk
    cur.execute("SELECT COUNT(*) FROM products")
    total_products = cur.fetchone()[0]

    # Transaksi & total hari ini
    cur.execute("""
        SELECT COUNT(*), IFNULL(SUM(total), 0)
        FROM sales
        WHERE DATE(sale_date) = DATE('now', 'localtime')
    """)
    total_sales, total_revenue = cur.fetchone()

    conn.close()

    return {
        "products": total_products,
        "sales_today": total_sales,
        "revenue_today": total_revenue
    }


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

def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor()

    # Jumlah produk
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # Transaksi hari ini
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM sales WHERE sale_date = ?", (today,))
    sales_today, revenue_today = cursor.fetchone()

    conn.close()
    return {
        "products": total_products,
        "sales_today": sales_today,
        "revenue_today": revenue_today
    }

# ==========================================================
# Fungsi ini untuk chart pendapatan 3 bulan terakhir
# ==========================================================
def get_last_3_months_revenue():
    conn = get_connection()
    cursor = conn.cursor()

    data = []
    today = datetime.now()

    # Ambil 3 bulan terakhir sebelum bulan ini
    for i in range(3, 0, -1):
        # Dapatkan awal bulan i bulan lalu
        month_date = today.replace(day=1) - timedelta(days=30 * i)
        year_month = month_date.strftime("%Y-%m")

        cursor.execute("""
            SELECT COALESCE(SUM(total), 0)
            FROM sales
            WHERE strftime('%Y-%m', sale_date) = ?
        """, (year_month,))

        total = cursor.fetchone()[0]
        data.append({
            "month": month_date.strftime("%B"),  # contoh: "Juli"
            "revenue": total
        })

    conn.close()
    return data
