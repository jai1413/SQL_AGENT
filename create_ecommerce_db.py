# create_ecommerce_db.py
import sqlite3

conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# ── Tables ──────────────────────────────────────────────
cursor.executescript("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    city TEXT,
    country TEXT,
    joined_date TEXT
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    price REAL,
    stock INTEGER
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    order_date TEXT,
    status TEXT,
    total REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price REAL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    product_id INTEGER,
    rating INTEGER,
    comment TEXT,
    review_date TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
""")

# ── Customers ────────────────────────────────────────────
cursor.executemany("INSERT INTO customers (name, email, city, country, joined_date) VALUES (?,?,?,?,?)", [
    ("Alice Johnson",  "alice@email.com",  "New York",    "USA",   "2022-01-15"),
    ("Bob Smith",      "bob@email.com",    "London",      "UK",    "2022-03-22"),
    ("Carol White",    "carol@email.com",  "Toronto",     "CA",    "2022-05-10"),
    ("David Lee",      "david@email.com",  "Sydney",      "AU",    "2022-07-18"),
    ("Eva Martinez",   "eva@email.com",    "Madrid",      "ES",    "2022-09-05"),
    ("Frank Brown",    "frank@email.com",  "Chicago",     "USA",   "2023-01-12"),
    ("Grace Kim",      "grace@email.com",  "Seoul",       "KR",    "2023-03-08"),
    ("Henry Wilson",   "henry@email.com",  "Berlin",      "DE",    "2023-05-20"),
    ("Isla Thompson",  "isla@email.com",   "Dubai",       "UAE",   "2023-07-14"),
    ("Jack Davis",     "jack@email.com",   "Singapore",   "SG",    "2023-09-30"),
])

# ── Products ─────────────────────────────────────────────
cursor.executemany("INSERT INTO products (name, category, price, stock) VALUES (?,?,?,?)", [
    ("Laptop Pro 15",       "Electronics",   1299.99,  30),
    ("Wireless Mouse",      "Electronics",     29.99, 150),
    ("Mechanical Keyboard", "Electronics",     89.99,  75),
    ("USB-C Hub",           "Electronics",     49.99, 100),
    ("Running Shoes",       "Footwear",        79.99,  60),
    ("Yoga Mat",            "Sports",          25.99,  90),
    ("Protein Powder",      "Health",          45.99,  50),
    ("Backpack 30L",        "Accessories",     59.99,  40),
    ("Sunglasses UV400",    "Accessories",     34.99,  80),
    ("Python Book",         "Books",           39.99, 200),
    ("Desk Lamp LED",       "Home",            22.99, 120),
    ("Coffee Maker",        "Home",            89.99,  35),
])

# ── Orders ───────────────────────────────────────────────
cursor.executemany("INSERT INTO orders (customer_id, order_date, status, total) VALUES (?,?,?,?)", [
    (1,  "2024-01-05", "delivered",  1329.98),
    (1,  "2024-03-12", "delivered",    89.99),
    (2,  "2024-01-20", "delivered",   139.98),
    (3,  "2024-02-14", "delivered",   125.98),
    (4,  "2024-02-28", "shipped",     299.99),
    (5,  "2024-03-05", "delivered",    71.98),
    (6,  "2024-03-18", "processing",  149.98),
    (7,  "2024-04-01", "delivered",    65.98),
    (8,  "2024-04-10", "shipped",      89.99),
    (9,  "2024-04-22", "delivered",   104.98),
    (10, "2024-05-01", "processing",   79.99),
    (2,  "2024-05-10", "delivered",    45.99),
])

# ── Order Items ──────────────────────────────────────────
cursor.executemany("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?,?,?,?)", [
    (1,  1, 1, 1299.99),  # Alice → Laptop
    (1,  2, 1,   29.99),  # Alice → Mouse
    (2,  3, 1,   89.99),  # Alice → Keyboard
    (3,  2, 1,   29.99),  # Bob   → Mouse
    (3,  4, 1,   49.99),  # Bob   → USB Hub
    (4,  6, 1,   25.99),  # Carol → Yoga Mat
    (4,  5, 1,   79.99),  # Carol → Shoes
    (5,  1, 1, 1299.99),  # David → Laptop  (only item, order total mismatch ok for demo)
    (6,  9, 1,   34.99),  # Eva   → Sunglasses
    (6,  11,1,   22.99),  # Eva   → Desk Lamp
    (7,  10,1,   39.99),  # Frank → Python Book
    (7,  7, 1,   45.99),  # Frank → Protein Powder  (partial)
    (8,  6, 2,   25.99),  # Grace → 2x Yoga Mat
    (9,  3, 1,   89.99),  # Henry → Keyboard
    (10, 9, 1,   34.99),  # Isla  → Sunglasses
    (10, 8, 1,   59.99),  # Isla  → Backpack
    (11, 5, 1,   79.99),  # Jack  → Shoes
    (12, 7, 1,   45.99),  # Bob   → Protein Powder
])

# ── Reviews ──────────────────────────────────────────────
cursor.executemany("INSERT INTO reviews (customer_id, product_id, rating, comment, review_date) VALUES (?,?,?,?,?)", [
    (1,  1, 5, "Fantastic laptop, worth every penny!",     "2024-01-20"),
    (1,  2, 4, "Smooth and responsive.",                   "2024-01-21"),
    (2,  2, 3, "Decent mouse but scroll wheel is noisy.",  "2024-02-01"),
    (3,  6, 5, "Best yoga mat I've ever used!",            "2024-02-20"),
    (4,  1, 4, "Great performance, runs hot sometimes.",   "2024-03-10"),
    (5,  9, 5, "Stylish and great UV protection.",         "2024-03-15"),
    (6,  10,5, "Excellent Python book for beginners.",     "2024-04-01"),
    (7,  6, 4, "Good grip, slightly thin.",                "2024-04-10"),
    (8,  3, 5, "Clicky and satisfying to type on!",        "2024-04-18"),
    (10, 5, 4, "Comfortable for long runs.",               "2024-05-05"),
])

conn.commit()
conn.close()
print("✅ Ecommerce DB created successfully!")