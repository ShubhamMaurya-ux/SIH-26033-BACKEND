import sqlite3

connection = sqlite3.connect("database.db")

cursor = connection.cursor()

# Farmers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS farmers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    location TEXT NOT NULL
)
""")

# Products table
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

connection.commit()
connection.close()