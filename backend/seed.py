"""
Seed the database with 20 realistic marketplace items.

Usage:
    python seed.py
"""

from database import init_db, get_db

ITEMS = [
    # ---- Books (5) ----
    {
        "title": "Introduction to Algorithms (Cormen, 4th ed.)",
        "description": "Hardcover, some highlighting in chapters 1-12. Classic CLRS textbook.",
        "price": 35.00,
        "category": "Books",
        "image_url": None,
        "seller_name": "Alice Martin",
        "is_sold": 0,
    },
    {
        "title": "Clean Code — Robert C. Martin",
        "description": "Paperback, like new. Essential reading for software engineers.",
        "price": 18.50,
        "category": "Books",
        "image_url": None,
        "seller_name": "Lucas Dupont",
        "is_sold": 0,
    },
    {
        "title": "Design Patterns (Gang of Four)",
        "description": "Hardcover, first edition reprint. Minor wear on spine.",
        "price": 22.00,
        "category": "Books",
        "image_url": None,
        "seller_name": "Emma Bernard",
        "is_sold": 1,
    },
    {
        "title": "The Pragmatic Programmer (20th Anniversary)",
        "description": "Perfect condition, never opened. Bought two copies by mistake.",
        "price": 25.00,
        "category": "Books",
        "image_url": None,
        "seller_name": "Hugo Leroy",
        "is_sold": 0,
    },
    {
        "title": "Operating Systems: Three Easy Pieces",
        "description": "Printed version of the free online book. Spiral-bound.",
        "price": 10.00,
        "category": "Books",
        "image_url": None,
        "seller_name": "Chloe Moreau",
        "is_sold": 0,
    },
    # ---- Electronics (5) ----
    {
        "title": "Logitech MX Master 3S Mouse",
        "description": "Graphite, used for 6 months. Includes USB-C cable and dongle.",
        "price": 55.00,
        "category": "Electronics",
        "image_url": None,
        "seller_name": "Nathan Petit",
        "is_sold": 0,
    },
    {
        "title": "Samsung 27\" 4K Monitor (U28E590D)",
        "description": "Great for coding. One dead pixel in bottom-right corner, barely visible.",
        "price": 150.00,
        "category": "Electronics",
        "image_url": None,
        "seller_name": "Lea Roux",
        "is_sold": 0,
    },
    {
        "title": "Keychron K2 Mechanical Keyboard (Brown switches)",
        "description": "Wireless, hot-swappable. Comes with original keycaps + extra set.",
        "price": 65.00,
        "category": "Electronics",
        "image_url": None,
        "seller_name": "Alice Martin",
        "is_sold": 1,
    },
    {
        "title": "Raspberry Pi 4 (4 GB) + Case",
        "description": "Includes power supply and 32 GB SD card with Raspbian.",
        "price": 40.00,
        "category": "Electronics",
        "image_url": None,
        "seller_name": "Hugo Leroy",
        "is_sold": 0,
    },
    {
        "title": "Apple AirPods Pro (2nd gen) — Left bud only",
        "description": "Lost the right one. Left bud + case work perfectly.",
        "price": 45.00,
        "category": "Electronics",
        "image_url": None,
        "seller_name": "Emma Bernard",
        "is_sold": 0,
    },
    # ---- Furniture (5) ----
    {
        "title": "IKEA KALLAX Shelf Unit (2x4, white)",
        "description": "Good condition, minor scratches on top. Pick-up only at Villejuif.",
        "price": 30.00,
        "category": "Furniture",
        "image_url": None,
        "seller_name": "Lucas Dupont",
        "is_sold": 0,
    },
    {
        "title": "Adjustable Standing Desk (120x60 cm)",
        "description": "Electric height-adjustable. White top, black frame. 2 years old.",
        "price": 180.00,
        "category": "Furniture",
        "image_url": None,
        "seller_name": "Nathan Petit",
        "is_sold": 1,
    },
    {
        "title": "Ergonomic Office Chair (mesh back)",
        "description": "Brand: Autonomous ErgoChair. Lumbar support, adjustable armrests.",
        "price": 120.00,
        "category": "Furniture",
        "image_url": None,
        "seller_name": "Chloe Moreau",
        "is_sold": 0,
    },
    {
        "title": "Desk Lamp — LED with USB charging port",
        "description": "3 brightness levels, flexible arm. Great for late-night coding.",
        "price": 15.00,
        "category": "Furniture",
        "image_url": None,
        "seller_name": "Lea Roux",
        "is_sold": 0,
    },
    {
        "title": "IKEA LACK Coffee Table (black)",
        "description": "Barely used, moving out of dorm. You pick up.",
        "price": 8.00,
        "category": "Furniture",
        "image_url": None,
        "seller_name": "Hugo Leroy",
        "is_sold": 0,
    },
    # ---- Clothing (5) ----
    {
        "title": "EPITA Hoodie — Promo 2027 (size M)",
        "description": "Official promo hoodie, black with white logo. Worn twice.",
        "price": 20.00,
        "category": "Clothing",
        "image_url": None,
        "seller_name": "Alice Martin",
        "is_sold": 0,
    },
    {
        "title": "North Face Puffer Jacket (size L, navy)",
        "description": "Warm and lightweight. Perfect for Paris winters.",
        "price": 75.00,
        "category": "Clothing",
        "image_url": None,
        "seller_name": "Nathan Petit",
        "is_sold": 1,
    },
    {
        "title": "Converse Chuck Taylor All-Stars (size 42, white)",
        "description": "Classic high-tops, worn a few times. Cleaned and ready.",
        "price": 28.00,
        "category": "Clothing",
        "image_url": None,
        "seller_name": "Emma Bernard",
        "is_sold": 0,
    },
    {
        "title": "Levi's 501 Jeans (W32 L32, dark blue)",
        "description": "Straight fit, excellent condition.",
        "price": 30.00,
        "category": "Clothing",
        "image_url": None,
        "seller_name": "Lucas Dupont",
        "is_sold": 0,
    },
    {
        "title": "Patagonia Fleece Pullover (size S, grey)",
        "description": "Better Sweater model. Super cozy, no pilling.",
        "price": 50.00,
        "category": "Clothing",
        "image_url": None,
        "seller_name": "Chloe Moreau",
        "is_sold": 0,
    },
]


def seed():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    # Only seed if the table is empty
    cursor.execute("SELECT COUNT(*) FROM items")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Database already contains {count} items — skipping seed.")
        cursor.close()
        conn.close()
        return

    for item in ITEMS:
        cursor.execute(
            """
            INSERT INTO items (title, description, price, category, image_url, seller_name, is_sold)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                item["title"],
                item["description"],
                item["price"],
                item["category"],
                item["image_url"],
                item["seller_name"],
                item["is_sold"],
            ),
        )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Seeded {len(ITEMS)} items into the database.")


def seed_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sellers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("DELETE FROM sellers")
    sellers = [
        ("admin", "admin123", "admin@marketplace.epita.fr"),
        ("alice_martin", "password", "alice.martin@epita.fr"),
        ("lucas_dupont", "lucas2026", "lucas.dupont@epita.fr"),
    ]
    for username, password, email in sellers:
        cursor.execute(
            "INSERT INTO sellers (username, password, email) VALUES (%s, %s, %s)",
            (username, password, email),
        )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Seeded {len(sellers)} sellers.")


if __name__ == "__main__":
    seed()
    seed_users()
