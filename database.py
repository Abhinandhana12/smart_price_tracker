import sqlite3
from datetime import datetime

DB_PATH = 'price_tracker.db'

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            current_price REAL,
            target_price REAL NOT NULL,
            email TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price REAL NOT NULL,
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    conn.commit()
    conn.close()

def add_product(name, url, current_price, target_price, email):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        INSERT INTO products (name, url, current_price, target_price, email)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, url, current_price, target_price, email))
    product_id = c.lastrowid
    c.execute('''
        INSERT INTO price_history (product_id, price) VALUES (?, ?)
    ''', (product_id, current_price))
    conn.commit()
    conn.close()
    return product_id

def get_all_products():
    conn = get_conn()
    c = conn.cursor()
    rows = c.execute('SELECT * FROM products ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_price(product_id, price):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE products SET current_price = ? WHERE id = ?', (price, product_id))
    c.execute('INSERT INTO price_history (product_id, price) VALUES (?, ?)', (product_id, price))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM price_history WHERE product_id = ?', (product_id,))
    c.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

def get_price_history(product_id):
    conn = get_conn()
    c = conn.cursor()
    rows = c.execute('''
        SELECT price, recorded_at FROM price_history
        WHERE product_id = ? ORDER BY recorded_at ASC
    ''', (product_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
