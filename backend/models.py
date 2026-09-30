"""
Pydantic models and database query functions for items.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from database import get_db


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ItemCreate(BaseModel):
    """Schema used when creating a new item (POST body)."""

    # strip leading and trailing whitespace before length is validated
    # rejects unknown fields as well
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=1)
    image_url: Optional[str] = None
    seller_name: str = Field(..., min_length=1)


class ItemOut(BaseModel):
    """Schema returned to clients."""
    id: int
    title: str
    description: Optional[str]
    price: float
    category: str
    image_url: Optional[str]
    seller_name: str
    created_at: str
    is_sold: bool

class CategoryOut(BaseModel):
    """Category schema returned to clients."""
    category_name: str
    category_count: int


# ---------------------------------------------------------------------------
# Items DB helpers
# ---------------------------------------------------------------------------

def _serialize_row(row) -> dict:
    """Convert a row dict, handling datetime and is_sold conversion."""
    if row is None:
        return None
    d = dict(row)
    d["is_sold"] = bool(d.get("is_sold", 0))
    for key, value in d.items():
        if hasattr(value, 'isoformat'):
            d[key] = value.isoformat()
    return d


def get_all_items(category: Optional[str] = None) -> List[dict]:
    """Return every item, newest first."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        if category:
            cursor.execute(
                "SELECT * FROM items WHERE category = %s ORDER BY created_at DESC",
                (category,),
            )
        else:
            cursor.execute("SELECT * FROM items ORDER BY created_at DESC")

        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return [_serialize_row(r) for r in rows]


def get_item_by_id(item_id: int) -> Optional[dict]:
    """Return a single item or None."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM items WHERE id = %s", (item_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row is None:
        return None
    return _serialize_row(row)


def create_item(item: ItemCreate) -> dict:
    """Insert a new item and return it (with generated id and timestamp)."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        INSERT INTO items (title, description, price, category, image_url, seller_name)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            item.title,
            item.description,
            item.price,
            item.category,
            item.image_url,
            item.seller_name,
        ),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM items WHERE id = %s", (new_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return _serialize_row(row)

# ---------------------------------------------------------------------------
# Category DB helpers
# ---------------------------------------------------------------------------

def _category_serialize_row(row) -> Optional[dict]:
    """Convert a category row dict"""
    if row is None:
        return None

    d = dict(row)

    return d

def get_all_categories() -> List[dict]:
    """Return every category, with the highest count first."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                i.category AS category_name,
                COUNT(*) AS category_count
            FROM items i
            GROUP BY i.category
            ORDER BY category_count DESC;
        """)

        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    serialized_rows = []

    for r in rows:
        serialized_row = _category_serialize_row(r)

        if serialized_row:
            serialized_rows.append(serialized_row)

    return serialized_rows