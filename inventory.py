
import sqlite3
from database import connect_db


# 1. Add New Product
def add_product(name, category, price, quantity, min_stock):

    # Input Validation
    if not name.strip():
        raise ValueError("Product name cannot be empty.")

    if not category.strip():
        raise ValueError("Category cannot be empty.")

    if price < 0:
        raise ValueError("Price cannot be negative.")

    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")

    if min_stock < 0:
        raise ValueError("Minimum stock cannot be negative.")

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO products
            (name, category, price, quantity, min_stock)
            VALUES (?, ?, ?, ?, ?)
        """, (name.strip(), category.strip(), price, quantity, min_stock))

        conn.commit()

    finally:
        conn.close()

# 2. View All Products
def view_products():

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    conn.close()

    return products


# 3. Search Product
def search_product(keyword):

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE name LIKE ? OR category LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%"))

    products = cursor.fetchall()

    conn.close()

    return products


# 4. Update Product
def update_product(product_id, name, category, price, min_stock):

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET name=?, category=?, price=?, min_stock=?
        WHERE product_id=?
    """, (name, category, price, min_stock, product_id))

    conn.commit()

    conn.close()


# 5. Delete Product
def delete_product(product_id):

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM products WHERE product_id=?",
        (product_id,)
    )

    cursor.execute(
        "DELETE FROM stock_history WHERE product_id=?",
        (product_id,)
    )

    conn.commit()

    conn.close()


# 6. Stock In
def stock_in(product_id, quantity):

    if quantity <= 0:
        raise ValueError("Stock quantity must be greater than zero.")

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE products
            SET quantity = quantity + ?
            WHERE product_id = ?
        """, (quantity, product_id))

        if cursor.rowcount == 0:
            raise ValueError("Product not found.")

        cursor.execute("""
            INSERT INTO stock_history
            (product_id, transaction_type, quantity)
            VALUES (?, 'STOCK IN', ?)
        """, (product_id, quantity))

        conn.commit()

    finally:
        conn.close()


# 7. Stock Out
def stock_out(product_id, quantity):

    if quantity <= 0:
        raise ValueError("Stock quantity must be greater than zero.")

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE products
            SET quantity = quantity - ?
            WHERE product_id = ? AND quantity >= ?
        """, (quantity, product_id, quantity))

        if cursor.rowcount == 0:
            return False

        cursor.execute("""
            INSERT INTO stock_history
            (product_id, transaction_type, quantity)
            VALUES (?, 'STOCK OUT', ?)
        """, (product_id, quantity))

        conn.commit()
        return True

    finally:
        conn.close()


# 8. Low Stock Products
def low_stock_products():

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE quantity <= min_stock
    """)

    products = cursor.fetchall()

    conn.close()

    return products
