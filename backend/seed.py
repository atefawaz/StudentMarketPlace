"""
Seed the database with 20 realistic marketplace items.

Usage:
    python seed.py
"""

from dotenv import load_dotenv

from database import init_db, get_db
from auth import hash_password
from utilities import get_required_env

load_dotenv()

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

SELLERS = [
    {
        "username": "admin",
        "display_name": "Admin",
        "email": "admin@marketplace.epita.fr",
        "password_env": "SEED_ADMIN_PASSWORD",
    },
    {
        "username": "alice_martin",
        "display_name": "Alice Martin",
        "email": "alice.martin@epita.fr",
        "password_env": "SEED_ALICE_PASSWORD",
    },
    {
        "username": "lucas_dupont",
        "display_name": "Lucas Dupont",
        "email": "lucas.dupont@epita.fr",
        "password_env": "SEED_LUCAS_PASSWORD",
    },
    {
        "username": "emma_bernard",
        "display_name": "Emma Bernard",
        "email": "emma.bernard@epita.fr",
        "password_env": "SEED_DEFAULT_PASSWORD",
    },
    {
        "username": "hugo_leroy",
        "display_name": "Hugo Leroy",
        "email": "hugo.leroy@epita.fr",
        "password_env": "SEED_DEFAULT_PASSWORD",
    },
    {
        "username": "chloe_moreau",
        "display_name": "Chloe Moreau",
        "email": "chloe.moreau@epita.fr",
        "password_env": "SEED_DEFAULT_PASSWORD",
    },
    {
        "username": "nathan_petit",
        "display_name": "Nathan Petit",
        "email": "nathan.petit@epita.fr",
        "password_env": "SEED_DEFAULT_PASSWORD",
    },
    {
        "username": "lea_roux",
        "display_name": "Lea Roux",
        "email": "lea.roux@epita.fr",
        "password_env": "SEED_DEFAULT_PASSWORD",
    },
]

def seed():
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Only seed if the table is empty
        cursor.execute("SELECT COUNT(*) FROM items")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Database already contains {count} items — skipping seed.")
            return

        cursor.execute("SELECT display_name, id FROM sellers")
        seller_ids = dict(cursor.fetchall())

        # Resolve every seller before inserting, so a typo can't leave a partial seed
        rows = []
        for item in ITEMS:
            seller_id = seller_ids.get(item["seller_name"])
            if seller_id is None:
                print(
                    f"No seller with display_name {item['seller_name']!r} ",
                    f"(needed by item {item['title']!r}). Add it to SELLERS."
                )
                continue
            rows.append(
                (
                    item["title"],
                    item["description"],
                    item["price"],
                    item["category"],
                    item["image_url"],
                    item["seller_name"],
                    seller_id,
                    item["is_sold"],
                )
            )

        cursor.executemany(
            """
            INSERT INTO items
                (title, description, price, category, image_url,
                 seller_name, seller_id, is_sold)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            rows,
        )
        conn.commit()
        print(f"Seeded {len(rows)} items into the database.")
    finally:
        cursor.close()
        conn.close()


def seed_users():
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username FROM sellers")
        existing = {row[0] for row in cursor.fetchall()}

        # Read env vars and hash before writing anything
        to_insert = [
            (
                s["username"],
                hash_password(get_required_env(s["password_env"])),
                s["display_name"],
                s["email"],
            )
            for s in SELLERS
            if s["username"] not in existing
        ]

        if not to_insert:
            print("All sellers already exist — skipping seed.")
            return

        cursor.executemany(
            """
            INSERT INTO sellers (username, password_hash, display_name, email)
            VALUES (%s, %s, %s, %s)
            """,
            to_insert,
        )
        conn.commit()
        print(f"Seeded {len(to_insert)} sellers.")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    init_db()
    seed_users()
    seed()
