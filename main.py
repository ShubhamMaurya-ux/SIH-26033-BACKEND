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

class ProductUpdate(BaseModel):
    name: str
    quantity: float
    price: float
    category: str

class FarmerUpdate(BaseModel):
    name: str
    phone: str
    location: str

class Order(BaseModel):
    product_id: int
    buyer_id: str
    quantity: float

class OrderStatusUpdate(BaseModel):
    status: str

class Buyer(BaseModel):
    name: str
    phone: str
    location: str

class BuyerUpdate(BaseModel):
    name: str
    phone: str
    location: str

class UserRegister(BaseModel):
    name: str
    phone: str
    password: str
    role: str

class UserLogin(BaseModel):
    phone: str
    password: str


@app.post("/register")
def register_user(user: UserRegister):
    connection = get_connection()
    cursor = connection.cursor()

    # Validate role
    if user.role not in ["farmer", "buyer"]:
        connection.close()
        return {
            "error": "Invalid role",
            "allowed_roles": ["farmer", "buyer"]
        }

    # Check whether phone already exists
    cursor.execute(
        "SELECT id FROM users WHERE phone = ?",
        (user.phone,)
    )

    if cursor.fetchone():
        connection.close()
        return {"error": "User with this phone already exists"}

    # Create user
    cursor.execute("""
        INSERT INTO users (name, phone, password, role)
        VALUES (?, ?, ?, ?)
    """, (
        user.name,
        user.phone,
        user.password,
        user.role
    ))

    user_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {
        "message": "User registered successfully",
        "user_id": user_id,
        "name": user.name,
        "phone": user.phone,
        "role": user.role
    }

@app.post("/login")
def login_user(user: UserLogin):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, phone, role
        FROM users
        WHERE phone = ? AND password = ?
    """, (user.phone, user.password))

    existing_user = cursor.fetchone()
    connection.close()

    if existing_user is None:
        return {"error": "Invalid phone or password"}

    return {
        "message": "Login successful",
        "user_id": existing_user[0],
        "name": existing_user[1],
        "phone": existing_user[2],
        "role": existing_user[3]
    }

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

@app.get("/products/category/{category}")
def get_products_by_category(category: str):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
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
        WHERE LOWER(products.category) = LOWER(?)
    """, (category,))

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

    return {"products": products}

@app.get("/products/location/{location}")
def get_products_by_location(location: str):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
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
        WHERE LOWER(farmers.location) = LOWER(?)
    """, (location,))

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

    return {"products": products}

@app.get("/products/available")
def get_available_products():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
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
        WHERE products.quantity > 0
    """)

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

    return {"products": products}

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

@app.put("/products/{product_id}")
def update_product(product_id: int, product: ProductUpdate):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE products
        SET name = ?,
            quantity = ?,
            price = ?,
            category = ?
        WHERE id = ?
    """, (
        product.name,
        product.quantity,
        product.price,
        product.category,
        product_id
    ))

    if cursor.rowcount == 0:
        connection.close()
        return {"error": "Product not found"}

    connection.commit()
    connection.close()

    return {
        "message": "Product updated successfully",
        "product_id": product_id
    }

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id = ?",
        (product_id,)
    )

    if cursor.rowcount == 0:
        connection.close()
        return {"error": "Product not found"}

    connection.commit()
    connection.close()

    return {
        "message": "Product deleted successfully",
        "product_id": product_id
    }

@app.put("/farmers/{farmer_id}")
def update_farmer(farmer_id: int, farmer: FarmerUpdate):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE farmers
        SET name = ?,
            phone = ?,
            location = ?
        WHERE id = ?
    """, (
        farmer.name,
        farmer.phone,
        farmer.location,
        farmer_id
    ))

    if cursor.rowcount == 0:
        connection.close()
        return {"error": "Farmer not found"}

    connection.commit()
    connection.close()

    return {
        "message": "Farmer updated successfully",
        "farmer_id": farmer_id
    }

@app.delete("/farmers/{farmer_id}")
def delete_farmer(farmer_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    # First delete products belonging to this farmer
    cursor.execute(
        "DELETE FROM products WHERE farmer_id = ?",
        (farmer_id,)
    )

    # Then delete the farmer
    cursor.execute(
        "DELETE FROM farmers WHERE id = ?",
        (farmer_id,)
    )

    if cursor.rowcount == 0:
        connection.close()
        return {"error": "Farmer not found"}

    connection.commit()
    connection.close()

    return {
        "message": "Farmer and their products deleted successfully",
        "farmer_id": farmer_id
    }

@app.put("/products/{product_id}/stock")
def update_stock(product_id: int, quantity_sold: float):
    connection = get_connection()
    cursor = connection.cursor()

    # Check current stock
    cursor.execute(
        "SELECT quantity FROM products WHERE id = ?",
        (product_id,)
    )

    product = cursor.fetchone()

    if product is None:
        connection.close()
        return {"error": "Product not found"}

    current_quantity = product[0]

    if quantity_sold <= 0:
        connection.close()
        return {"error": "Quantity sold must be greater than 0"}

    if quantity_sold > current_quantity:
        connection.close()
        return {"error": "Not enough stock available"}

    new_quantity = current_quantity - quantity_sold

    cursor.execute(
        "UPDATE products SET quantity = ? WHERE id = ?",
        (new_quantity, product_id)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Stock updated successfully",
        "product_id": product_id,
        "old_quantity": current_quantity,
        "quantity_sold": quantity_sold,
        "remaining_quantity": new_quantity
    }


# =========================
# ORDERS TABLE
# =========================

@app.post("/orders")
def create_order(order: Order):
    connection = get_connection()
    cursor = connection.cursor()

    # Check buyer
    cursor.execute(
        "SELECT id, name, phone FROM buyers WHERE id = ?",
        (order.buyer_id,)
    )

    buyer = cursor.fetchone()

    if buyer is None:
        connection.close()
        return {"error": "Buyer not found"}

    # Check product
    cursor.execute(
        "SELECT name, price, quantity FROM products WHERE id = ?",
        (order.product_id,)
    )

    product = cursor.fetchone()

    if product is None:
        connection.close()
        return {"error": "Product not found"}

    product_name, price, available_quantity = product

    # Validate quantity
    if order.quantity <= 0:
        connection.close()
        return {"error": "Order quantity must be greater than 0"}

    if order.quantity > available_quantity:
        connection.close()
        return {"error": "Not enough stock available"}

    # Calculate total
    total_price = order.quantity * price

    # Create order
    cursor.execute("""
        INSERT INTO orders
        (product_id, buyer_id, buyer_name, buyer_phone,
         quantity, total_price, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        order.product_id,
        order.buyer_id,
        buyer[1],
        buyer[2],
        order.quantity,
        total_price,
        "Pending"
    ))

    order_id = cursor.lastrowid

    # Reduce stock
    new_quantity = available_quantity - order.quantity

    cursor.execute(
        "UPDATE products SET quantity = ? WHERE id = ?",
        (new_quantity, order.product_id)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Order placed successfully",
        "order_id": order_id,
        "buyer_id": order.buyer_id,
        "buyer_name": buyer[1],
        "product": product_name,
        "quantity": order.quantity,
        "total_price": total_price,
        "remaining_stock": new_quantity,
        "status": "Pending"
    }

@app.get("/orders")
def get_orders():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            orders.id,
            orders.product_id,
            products.name,
            orders.buyer_id,
            buyers.name,
            buyers.phone,
            buyers.location,
            orders.quantity,
            orders.total_price,
            orders.status
        FROM orders
        JOIN products
            ON orders.product_id = products.id
        JOIN buyers
            ON orders.buyer_id = buyers.id
        ORDER BY orders.id DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    orders = []

    for row in rows:
        orders.append({
            "order_id": row[0],
            "product_id": row[1],
            "product_name": row[2],
            "buyer_id": row[3],
            "buyer_name": row[4],
            "buyer_phone": row[5],
            "buyer_location": row[6],
            "quantity": row[7],
            "total_price": row[8],
            "status": row[9]
        })

    return {"orders": orders}

@app.put("/orders/{order_id}/status")
def update_order_status(order_id: int, order: OrderStatusUpdate):
    connection = get_connection()
    cursor = connection.cursor()

    allowed_statuses = ["Pending", "Confirmed", "Completed", "Cancelled"]

    if order.status not in allowed_statuses:
        connection.close()
        return {
            "error": "Invalid status",
            "allowed_statuses": allowed_statuses
        }

    # Get current order information
    cursor.execute("""
        SELECT product_id, quantity, status
        FROM orders
        WHERE id = ?
    """, (order_id,))

    existing_order = cursor.fetchone()

    if existing_order is None:
        connection.close()
        return {"error": "Order not found"}

    product_id, order_quantity, current_status = existing_order

    # Check valid status transitions
    valid_transitions = {
        "Pending": ["Confirmed", "Cancelled"],
        "Confirmed": ["Completed", "Cancelled"],
        "Completed": [],
        "Cancelled": []
    }

    if order.status not in valid_transitions[current_status]:
        connection.close()
        return {
            "error": "Invalid status transition",
            "current_status": current_status,
            "requested_status": order.status
        }

    # If already cancelled, don't restore stock again
    if current_status == "Cancelled":
        if order.status == "Cancelled":
            connection.close()
            return {
                "message": "Order is already cancelled",
                "order_id": order_id,
                "status": "Cancelled"
            }

        connection.close()
        return {
            "error": "Cancelled order cannot be changed"
        }

    # If cancelling, restore the ordered quantity
    if order.status == "Cancelled":
        cursor.execute("""
            UPDATE products
            SET quantity = quantity + ?
            WHERE id = ?
        """, (order_quantity, product_id))

    cursor.execute("""
        UPDATE orders
        SET status = ?
        WHERE id = ?
    """, (order.status, order_id))

    connection.commit()
    connection.close()

    return {
        "message": "Order status updated successfully",
        "order_id": order_id,
        "status": order.status
    }

@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM orders WHERE id = ?",
        (order_id,)
    )

    existing_order = cursor.fetchone()

    if existing_order is None:
        connection.close()
        return {"error": "Order not found"}

    cursor.execute(
        "DELETE FROM orders WHERE id = ?",
        (order_id,)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Order deleted successfully",
        "order_id": order_id
    }

@app.post("/buyers")
def create_buyer(buyer: Buyer):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM buyers WHERE phone = ?",
        (buyer.phone,)
    )

    existing_buyer = cursor.fetchone()

    if existing_buyer:
        connection.close()
        return {"error": "Buyer with this phone already exists"}

    cursor.execute("""
        INSERT INTO buyers (name, phone, location)
        VALUES (?, ?, ?)
    """, (
        buyer.name,
        buyer.phone,
        buyer.location
    ))

    buyer_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {
        "message": "Buyer created successfully",
        "buyer_id": buyer_id,
        "name": buyer.name,
        "phone": buyer.phone,
        "location": buyer.location
    }

@app.get("/buyers")
def get_buyers():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, phone, location
        FROM buyers
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    buyers = []

    for row in rows:
        buyers.append({
            "id": row[0],
            "name": row[1],
            "phone": row[2],
            "location": row[3]
        })

    return {"buyers": buyers}

@app.get("/buyers/{buyer_id}")
def get_buyer(buyer_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, phone, location
        FROM buyers
        WHERE id = ?
    """, (buyer_id,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return {"error": "Buyer not found"}

    return {
        "id": row[0],
        "name": row[1],
        "phone": row[2],
        "location": row[3]
    }

@app.put("/buyers/{buyer_id}")
def update_buyer(buyer_id: int, buyer: BuyerUpdate):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE buyers
        SET name = ?,
            phone = ?,
            location = ?
        WHERE id = ?
    """, (
        buyer.name,
        buyer.phone,
        buyer.location,
        buyer_id
    ))

    if cursor.rowcount == 0:
        connection.close()
        return {"error": "Buyer not found"}

    connection.commit()
    connection.close()

    return {
        "message": "Buyer updated successfully",
        "buyer_id": buyer_id
    }

@app.delete("/buyers/{buyer_id}")
def delete_buyer(buyer_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM buyers WHERE id = ?",
        (buyer_id,)
    )

    existing_buyer = cursor.fetchone()

    if existing_buyer is None:
        connection.close()
        return {"error": "Buyer not found"}

    cursor.execute(
        "DELETE FROM buyers WHERE id = ?",
        (buyer_id,)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Buyer deleted successfully",
        "buyer_id": buyer_id
    }

@app.get("/buyers/{buyer_id}/orders")
def get_buyer_orders(buyer_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    # Check buyer exists
    cursor.execute(
        "SELECT id FROM buyers WHERE id = ?",
        (buyer_id,)
    )

    if cursor.fetchone() is None:
        connection.close()
        return {"error": "Buyer not found"}

    cursor.execute("""
        SELECT
            orders.id,
            orders.product_id,
            products.name,
            orders.quantity,
            orders.total_price,
            orders.status
        FROM orders
        JOIN products
            ON orders.product_id = products.id
        WHERE orders.buyer_id = ?
        ORDER BY orders.id DESC
    """, (buyer_id,))

    rows = cursor.fetchall()
    connection.close()

    orders = []

    for row in rows:
        orders.append({
            "order_id": row[0],
            "product_id": row[1],
            "product_name": row[2],
            "quantity": row[3],
            "total_price": row[4],
            "status": row[5]
        })

    return {
        "buyer_id": buyer_id,
        "orders": orders
    }

@app.get("/farmers/{farmer_id}/orders")
def get_farmer_orders(farmer_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    # Check farmer exists
    cursor.execute(
        "SELECT id FROM farmers WHERE id = ?",
        (farmer_id,)
    )

    if cursor.fetchone() is None:
        connection.close()
        return {"error": "Farmer not found"}

    cursor.execute("""
        SELECT
            orders.id,
            orders.product_id,
            products.name,
            orders.buyer_id,
            buyers.name,
            buyers.phone,
            orders.quantity,
            orders.total_price,
            orders.status
        FROM orders
        JOIN products
            ON orders.product_id = products.id
        JOIN buyers
            ON orders.buyer_id = buyers.id
        WHERE products.farmer_id = ?
        ORDER BY orders.id DESC
    """, (farmer_id,))

    rows = cursor.fetchall()
    connection.close()

    orders = []

    for row in rows:
        orders.append({
            "order_id": row[0],
            "product_id": row[1],
            "product_name": row[2],
            "buyer_id": row[3],
            "buyer_name": row[4],
            "buyer_phone": row[5],
            "quantity": row[6],
            "total_price": row[7],
            "status": row[8]
        })

    return {
        "farmer_id": farmer_id,
        "orders": orders
    }

@app.get("/dashboard")
def get_dashboard():
    connection = get_connection()
    cursor = connection.cursor()

    # Total farmers
    cursor.execute("SELECT COUNT(*) FROM farmers")
    total_farmers = cursor.fetchone()[0]

    # Total buyers
    cursor.execute("SELECT COUNT(*) FROM buyers")
    total_buyers = cursor.fetchone()[0]

    # Total products
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # Total orders
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    # Total available stock
    cursor.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM products
        WHERE quantity > 0
    """)
    available_stock = cursor.fetchone()[0]

    # Total order value
    cursor.execute("""
        SELECT COALESCE(SUM(total_price), 0)
        FROM orders
        WHERE status != 'Cancelled'
    """)
    total_order_value = cursor.fetchone()[0]

    connection.close()

    return {
        "total_farmers": total_farmers,
        "total_buyers": total_buyers,
        "total_products": total_products,
        "total_orders": total_orders,
        "available_stock": available_stock,
        "total_order_value": total_order_value
    }