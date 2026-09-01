from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()


# =========================
# DATABASE CONNECTION
# =========================

def get_connection():
    return sqlite3.connect("database.db")


# =========================
# DATA MODELS
# =========================

class Product(BaseModel):
    farmer_id: int
    name: str
    category: str
    quantity: float
    price: float


class Farmer(BaseModel):
    name: str
    phone: str
    location: str


# =========================
# HOME
# =========================

@app.get("/")
def home():
    return {
        "message": "SIH 26033 Backend is running!"
    }


# =========================
# FARMER APIs
# =========================

# Add farmer
@app.post("/farmers")
def add_farmer(farmer: Farmer):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO farmers (name, phone, location)
        VALUES (?, ?, ?)
        """,
        (
            farmer.name,
            farmer.phone,
            farmer.location
        )
    )

    connection.commit()
    connection.close()

    return {
        "message": "Farmer registered successfully",
        "farmer": farmer
    }


# Get all farmers
@app.get("/farmers")
def get_farmers():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, phone, location FROM farmers"
    )

    rows = cursor.fetchall()

    connection.close()

    farmers = []

    for row in rows:
        farmers.append({
            "id": row[0],
            "name": row[1],
            "phone": row[2],
            "location": row[3]
        })

    return {
        "farmers": farmers
    }


# Get one farmer
@app.get("/farmers/{farmer_id}")
def get_farmer(farmer_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, phone, location
        FROM farmers
        WHERE id = ?
        """,
        (farmer_id,)
    )

    farmer = cursor.fetchone()

    connection.close()

    if farmer is None:
        return {
            "error": "Farmer not found"
        }

    return {
        "id": farmer[0],
        "name": farmer[1],
        "phone": farmer[2],
        "location": farmer[3]
    }


# Get products of one farmer
@app.get("/farmers/{farmer_id}/products")
def get_farmer_products(farmer_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    # Check farmer
    cursor.execute(
        """
        SELECT id, name, location
        FROM farmers
        WHERE id = ?
        """,
        (farmer_id,)
    )

    farmer = cursor.fetchone()

    if farmer is None:
        connection.close()

        return {
            "error": "Farmer not found"
        }

    # Get products
    cursor.execute(
        """
        SELECT id, name, category, quantity, price
        FROM products
        WHERE farmer_id = ?
        """,
        (farmer_id,)
    )

    rows = cursor.fetchall()

    connection.close()

    products = []

    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "quantity": row[3],
            "price": row[4]
        })

    return {
        "farmer": {
            "id": farmer[0],
            "name": farmer[1],
            "location": farmer[2]
        },
        "products": products
    }


# =========================
# PRODUCT APIs
# =========================

# Add product
@app.post("/products")
def add_product(product: Product):

    connection = get_connection()
    cursor = connection.cursor()

    # Check if farmer exists
    cursor.execute(
        "SELECT id FROM farmers WHERE id = ?",
        (product.farmer_id,)
    )

    farmer = cursor.fetchone()

    if farmer is None:
        connection.close()

        return {
            "error": "Farmer not found"
        }

    # Save product
    cursor.execute(
        """
        INSERT INTO products
        (farmer_id, name, category, quantity, price)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            product.farmer_id,
            product.name,
            product.category,
            product.quantity,
            product.price
        )
    )

    connection.commit()
    connection.close()

    return {
        "message": "Product saved successfully",
        "product": product
    }


# Get all products
@app.get("/products")
def get_products():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            products.id,
            products.farmer_id,
            farmers.name,
            farmers.location,
            products.name,
            products.category,
            products.quantity,
            products.price
        FROM products
        JOIN farmers
        ON products.farmer_id = farmers.id
        """
    )

    rows = cursor.fetchall()

    connection.close()

    products = []

    for row in rows:
        products.append({
            "id": row[0],
            "farmer_id": row[1],
            "farmer_name": row[2],
            "location": row[3],
            "name": row[4],
            "category": row[5],
            "quantity": row[6],
            "price": row[7]
        })

    return {
        "products": products
    }


# =========================
# SEARCH API
# =========================

@app.get("/search")
def search_products(name: str):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            products.id,
            products.farmer_id,
            farmers.name,
            farmers.location,
            products.name,
            products.category,
            products.quantity,
            products.price
        FROM products
        JOIN farmers
        ON products.farmer_id = farmers.id
        WHERE products.name LIKE ?
        """,
        (f"%{name}%",)
    )

    rows = cursor.fetchall()

    connection.close()

    results = []

    for row in rows:
        results.append({
            "id": row[0],
            "farmer_id": row[1],
            "farmer_name": row[2],
            "location": row[3],
            "product": row[4],
            "category": row[5],
            "quantity": row[6],
            "price": row[7]
        })

    return {
        "results": results
    }

