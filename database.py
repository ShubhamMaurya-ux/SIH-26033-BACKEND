import sqlite3

# Connect to database
connection = sqlite3.connect("database.db")

# Enable foreign keys
connection.execute("PRAGMA foreign_keys = ON")

cursor = connection.cursor()


# =========================
# FARMERS TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS farmers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    location TEXT NOT NULL
)
""")


# =========================
# PRODUCTS TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    quantity REAL NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id)
)
""")


# =========================
# ADD CATEGORY COLUMN
# =========================

# Check whether category column already exists
cursor.execute("PRAGMA table_info(products)")
columns = cursor.fetchall()

column_names = [column[1] for column in columns]

if "category" not in column_names:
    cursor.execute("""
        ALTER TABLE products
        ADD COLUMN category TEXT NOT NULL DEFAULT 'Other'
    """)

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    buyer_name TEXT NOT NULL,
    buyer_phone TEXT NOT NULL,
    quantity REAL NOT NULL,
    total_price REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (product_id) REFERENCES products(id)
)
""")

# =========================
# BUYERS TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS buyers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    location TEXT NOT NULL
)
""")

# =========================
# USERS TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# Save changes
connection.commit()

# Close database
connection.close()

