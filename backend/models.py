"""
Pydantic models and database query functions for items.
"""


from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    EmailStr,
    StringConstraints,
    field_validator
)
from typing import Optional, List, Annotated, cast
from database import get_db

import math

from mysql.connector import IntegrityError, errorcode

# ---------------------------------------------------------------------------
# Helper Constants
# ---------------------------------------------------------------------------

SORT_OPTIONS: dict = {
    "price_asc":  "price ASC, id ASC",
    "price_desc": "price DESC, id DESC",
    "date_asc":   "created_at ASC, id ASC",
    "date_desc":  "created_at DESC, id DESC",
}
DEFAULT_SORT: str = "date_desc"

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

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


class ItemOut(BaseModel):
    """Schema returned to clients."""
    id: int
    title: str
    description: Optional[str]
    price: float
    category: str
    image_url: Optional[str]
    seller_name: str
    seller_id: int
    created_at: str
    is_sold: bool

class CategoryOut(BaseModel):
    """Category schema returned to clients."""
    category_name: str
    category_count: int


class ItemSoldUpdate(BaseModel):
    """Schema used when updating an item to mark it as sold (PATCH body)."""
    is_sold: bool 

class RegisterRequest(BaseModel):
    """Body of POST /auth/register."""

    model_config = ConfigDict(extra="forbid")

    username: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_]+$")
    ]
    password: str = Field(..., min_length=8)
    display_name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)
    ]
    email: EmailStr

    @field_validator("username")
    @classmethod
    def lowercase_username(cls, v: str) -> str:
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, v:str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes")
        return v

class LoginRequest(BaseModel):
    """Body of POST /auth/login."""

    model_config = ConfigDict(extra="forbid")

    username: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)
    ]
    password: str = Field(..., min_length=1, max_length=255)

    @field_validator("username")
    @classmethod
    def lowercase_username(cls, v: str) -> str:
        return v.lower()

class SellerOut(BaseModel):
    """Seller schema returned to clients"""

    id: int
    username: str
    display_name: str
    email: str
    created_at: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PaginatedItemsOut(BaseModel):
    """Paginated list of items plus pagination metadata."""
    items: List[ItemOut]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

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

def _escape_like(value: str) -> str:
    """Escape LIKE wildcards so user input is matched literally."""
    return (
        value.replace("\\", "\\\\")
             .replace("%", "\\%")
             .replace("_", "\\_")
    )

def get_items_page(
    category: Optional[str] = None,
    sort: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> dict:
    """
    Return one page of items (optionally filtered by category / search and sorted,
    default: newest first) together with pagination metadata.
    """

    order_by = SORT_OPTIONS.get(sort, SORT_OPTIONS[DEFAULT_SORT])

    conditions: List[str] = []
    params: List[str] = []

    if category:
        conditions.append("category = %s")
        params.append(category)

    if search and search.strip():
        pattern = f"%{_escape_like(search.strip())}%"
        conditions.append("(title LIKE %s OR description LIKE %s)")
        params.extend([pattern, pattern])

    where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
    offset = (page - 1) * page_size

    count_query = f"SELECT COUNT(*) AS total FROM items{where}"
    items_query = (
        f"SELECT * FROM items{where} "
        f"ORDER BY {order_by}, id DESC LIMIT %s OFFSET %s"
    )

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(count_query, params)
        row = cursor.fetchone()
        # fetchone() is typed as a union of row shapes; with dictionary=True it is a dict
        total = cast(int, row["total"]) if isinstance(row, dict) else 0

        cursor.execute(items_query, params + [page_size, offset])
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    total_pages = math.ceil(total / page_size)

    return {
        "items": [_serialize_row(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


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


def create_item(item: ItemCreate, seller: dict) -> dict:
    """Insert a new item and return it (with generated id and timestamp)."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        INSERT INTO items (title, description, price, category, image_url, seller_name, seller_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            item.title,
            item.description,
            item.price,
            item.category,
            item.image_url,
            seller["display_name"],
            seller["id"],
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

# ---------------------------------------------------------------------------
# Sellers DB helpers
# ---------------------------------------------------------------------------

class UsernameTakenError(Exception):
    """Raised when the username violates the UNIQUE constraint."""

PUBLIC_COLUMNS = "id, username, display_name, email, created_at"

def _serialize_seller(row) -> Optional[dict]:
    if row is None:
        return None
    d = dict(row)
    if hasattr(d.get("created_at"), "isoformat"):
        d["created_at"] = d["created_at"].isoformat()
    return d

def create_seller(username: str, password_hash: str, display_name: str, email: str) -> dict:
    """Insert a seller and return it (without the hash)."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO sellers (username, password_hash, display_name, email)
            VALUES (%s, %s, %s, %s)
            """,
            (username, password_hash, display_name, email),
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute(f"SELECT {PUBLIC_COLUMNS} FROM sellers WHERE id = %s", (new_id,))
        row = cursor.fetchone()
    except IntegrityError as exc:
        # Relying on the UNIQUE constraint (instead of "check, then insert")
        # avoids a race between two simultaneous registrations.
        if exc.errno == errorcode.ER_DUP_ENTRY:
            raise UsernameTakenError(username) from exc
        raise
    finally:
        cursor.close()
        conn.close()

    serialized_seller = _serialize_seller(row)

    if serialized_seller is None:
        serialized_seller = dict()
    
    return serialized_seller

def get_seller_by_username(username: str) -> Optional[dict]:
    """Return a seller INCLUDING password_hash. Only use this for login."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"SELECT {PUBLIC_COLUMNS}, password_hash FROM sellers WHERE username = %s",
            (username,),
        )
        row = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
    return _serialize_seller(row)

def get_seller_by_id(seller_id: int) -> Optional[dict]:
    """Return a seller without the password hash."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(f"SELECT {PUBLIC_COLUMNS} FROM sellers WHERE id = %s", (seller_id,))
        row = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()
    return _serialize_seller(row)