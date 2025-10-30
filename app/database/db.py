# --- di app/database/db.py ---

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent.parent / "pos.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # products table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    # sales table (simple)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_date TEXT NOT NULL,
        total REAL NOT NULL
    )
    """)

    # sales_items table (line items)
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

    # posts (temporary / optional)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

# --- Product helpers ---

def insert_product(name: str, price: float, stock: int = 0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, price, stock, created_at) VALUES (?, ?, ?, ?)",
        (name, price, stock, datetime.utcnow().isoformat()),
    )
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

def get_all_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock FROM products ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    # return list of dicts for convenience
    return [{"id": r[0], "name": r[1], "price": r[2], "stock": r[3]} for r in rows]

def get_product_by_id(pid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock FROM products WHERE id = ?", (pid,))
    r = cur.fetchone()
    conn.close()
    if r:
        return {"id": r[0], "name": r[1], "price": r[2], "stock": r[3]}
    return None

def seed_products():
    """Tambahkan sample product jika belum ada"""
    if len(get_all_products()) == 0:
        insert_product("Pulpen Hitam", 1500.0, 100)
        insert_product("Buku Tulis A5", 12000.0, 50)
        insert_product("Penghapus", 2000.0, 200)
