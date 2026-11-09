import sqlite3
from datetime import datetime

import pandas as pd


def get_connection(path="shop.db"):
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY, name TEXT UNIQUE, price REAL, stock INTEGER)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        product_id INTEGER, quantity INTEGER, total REAL, sold_at TEXT,
        FOREIGN KEY (product_id) REFERENCES products(id))""")
    conn.commit()
    return conn


def get_products(conn):
    return pd.read_sql("SELECT id, name, price, stock FROM products ORDER BY name", conn)


def save_product(conn, name, price, stock):
    name = name.strip()
    if not name:
        raise ValueError("Product name is required.")
    if price < 0:
        raise ValueError("Price cannot be negative.")
    if stock < 0:
        raise ValueError("Stock cannot be negative.")
    with conn:
        conn.execute(
            """INSERT INTO products (name, price, stock) VALUES (?, ?, ?)
               ON CONFLICT(name) DO UPDATE SET price = excluded.price, stock = excluded.stock""",
            (name, price, stock),
        )


def record_sale(conn, product_id, qty):
    if qty < 1:
        raise ValueError("Quantity must be at least 1.")
    row = conn.execute(
        "SELECT price, stock FROM products WHERE id = ?", (product_id,)
    ).fetchone()
    if row is None:
        raise ValueError("Product not found.")
    price, stock = row
    if qty > stock:
        raise ValueError(f"Only {stock} in stock.")
    total = price * qty
    with conn:  # both changes succeed together, or neither happens
        conn.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, product_id))
        conn.execute(
            "INSERT INTO sales (product_id, quantity, total, sold_at) VALUES (?, ?, ?, ?)",
            (product_id, qty, total, datetime.now().isoformat(timespec="seconds")),
        )
    return total


def sales_today(conn):
    return pd.read_sql(
        """SELECT s.sold_at AS time, p.name AS product, s.quantity, s.total
           FROM sales s JOIN products p ON p.id = s.product_id
           WHERE date(s.sold_at) = date('now', 'localtime')
           ORDER BY s.sold_at DESC""",
        conn,
    )


def sales_history(conn):
    return pd.read_sql(
        """SELECT s.sold_at AS time, p.name AS product, s.quantity, s.total
           FROM sales s JOIN products p ON p.id = s.product_id
           ORDER BY s.sold_at DESC""",
        conn,
    )