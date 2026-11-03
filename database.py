
import sqlite3

def connect_db():
    conn = sqlite3.connect("inventory.db")
    return conn


def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            min_stock INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def create_stock_history():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            transaction_type TEXT,
            quantity INTEGER,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id)
            REFERENCES products(product_id)
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_table()
    create_stock_history()
    print("Database created successfully!")
