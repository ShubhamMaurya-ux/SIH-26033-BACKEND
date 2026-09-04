const API_URL = "http://127.0.0.1:8000";


// =========================
// PAGE NAVIGATION
// =========================

function showPage(pageId) {

    const pages = document.querySelectorAll(".page");

    pages.forEach(page => {
        page.classList.remove("active");
    });

    document.getElementById(pageId).classList.add("active");

    if (pageId === "products") {
        loadProducts();
    }
}


// =========================
// LOAD PRODUCTS
// =========================

async function loadProducts() {

    const productList = document.getElementById("product-list");

    productList.innerHTML = "<p>Loading products...</p>";

    try {

        const response = await fetch(`${API_URL}/products`);

        if (!response.ok) {
            throw new Error("Failed to load products");
        }

        const data = await response.json();

        const products = Array.isArray(data)
            ? data
            : data.products || [];

        if (products.length === 0) {
            productList.innerHTML =
                "<p>No products available.</p>";
            return;
        }

        productList.innerHTML = "";

        products.forEach(product => {

            const card = document.createElement("div");

            card.className = "product-card";

            card.innerHTML = `
                <h3>${product.name}</h3>

                <p>
                    <strong>Category:</strong>
                    ${product.category || "Not specified"}
                </p>

                <p>
                    <strong>Quantity:</strong>
                    ${product.quantity}
                </p>

                <p>
                    <strong>Price:</strong>
                    ₹${product.price}
                </p>
                ${localStorage.getItem("user_role") === "farmer"
                    ? `<button onclick="editProduct(${product.id})">✏️ Edit</button>`
                    : ""
                }
            `;

            productList.appendChild(card);
        });

    } catch (error) {

        console.error(error);

        productList.innerHTML = `
            <p>
                Unable to connect to the backend.
                Make sure FastAPI is running.
            </p>
        `;
    }
}


// =========================
// REGISTER
// =========================

async function registerUser(event) {

    event.preventDefault();

    const name =
        document.getElementById("register-name").value;

    const phone =
        document.getElementById("register-phone").value;

    const location =
        document.getElementById("register-location").value;

    const password =
        document.getElementById("register-password").value;

    const message =
        document.getElementById("register-message");


    try {

        const response = await fetch(
            `${API_URL}/farmers`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    name: name,
                    phone: phone,
                    location: location,
                    password: password
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            message.textContent =
                data.detail || "Registration failed.";

            return;
        }


        message.textContent =
            "Registration successful!";

        event.target.reset();

    } catch (error) {

        console.error(error);

        message.textContent =
            "Could not connect to backend.";
    }
}


// =========================
// LOGIN
// =========================

async function loginUser(event) {

    event.preventDefault();

    const phone =
        document.getElementById("login-phone").value;

    const password =
        document.getElementById("login-password").value;

    const message =
        document.getElementById("login-message");

    try {

        const response = await fetch(
            `${API_URL}/login`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    phone: phone,
                    password: password
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {

            message.textContent =
                data.detail || "Login failed.";

            return;
        }

        // Save logged-in user information
        localStorage.setItem(
            "user_id",
            data.user_id
        );

        localStorage.setItem(
            "user_name",
            data.name
        );

        localStorage.setItem(
            "user_role",
            data.role
        );

        message.textContent =
            `✅ Welcome ${data.name}!`;

        console.log("Logged in user:", data);

    } catch (error) {

        console.error(error);

        message.textContent =
            "❌ Could not connect to backend.";
    }
}
// =========================
// ADD PRODUCT
// =========================

async function addProduct(event) {

    event.preventDefault();

    const farmerId =
        document.getElementById("product-farmer-id").value;

    const name =
        document.getElementById("product-name").value;

    const category =
        document.getElementById("product-category").value;

    const quantity =
        document.getElementById("product-quantity").value;

    const price =
        document.getElementById("product-price").value;

    const message =
        document.getElementById("product-message");


    try {

        const response = await fetch(
            `${API_URL}/products`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    farmer_id: Number(farmerId),
                    name: name,
                    category: category || null,
                    quantity: Number(quantity),
                    price: Number(price)
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            message.textContent =
                data.detail || "Failed to add product.";

            return;
        }


        message.textContent =
            "✅ Product added successfully!";

        event.target.reset();

    } catch (error) {

        console.error(error);

        message.textContent =
            "❌ Could not connect to backend.";
    }
}

async function editProduct(productId) {

    const farmerId = localStorage.getItem("user_id");

    if (!farmerId) {
        alert("Please login first.");
        return;
    }

    const name = prompt("Enter new product name:");
    if (name === null) return;

    const quantity = prompt("Enter new quantity:");
    if (quantity === null) return;

    const price = prompt("Enter new price:");
    if (price === null) return;

    const category = prompt("Enter new category:");
    if (category === null) return;

    try {

        const response = await fetch(
            `${API_URL}/products/${productId}?farmer_id=${farmerId}`,
            {
                method: "PUT",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    name: name,
                    quantity: Number(quantity),
                    price: Number(price),
                    category: category
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || data.error || "Failed to update product.");
            return;
        }

        alert("✅ Product updated successfully!");

        loadProducts();

    } catch (error) {

        console.error(error);
        alert("❌ Could not connect to backend.");

    }
}