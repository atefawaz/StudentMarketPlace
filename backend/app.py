"""
Student Marketplace — FastAPI backend.

Run with:
    uvicorn app:app --reload --port 5000
"""

import logging
from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from dotenv import load_dotenv
from typing import Optional

from utilities import get_required_env

load_dotenv()

from database import init_db, get_db
from models import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    ItemCreate, 
    ItemOut, 
    CategoryOut,
    ItemSoldUpdate,
    LoginRequest,
    RegisterRequest,
    SellerOut,
    TokenOut,
    UsernameTakenError,
    PaginatedItemsOut,
    _serialize_row, 
    get_items_page, 
    get_item_by_id, 
    get_similar_items,
    create_item, 
    get_all_categories,
    create_seller,
    get_seller_by_username,
)

from auth import (
    DUMMY_HASH,
    create_token,
    get_current_user,
    hash_password,
    verify_password,
    require_item_owner,
)

app = FastAPI(
    title="Student Marketplace API",
    description="Buy and sell second-hand items on campus.",
    version="0.1.0",
)


class PoweredByMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Powered-By"] = "FastAPI/0.104.1 Python/3.11"
        return response


app.add_middleware(PoweredByMiddleware)

# Allow all origins so the Android / iOS emulators can reach the server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()

# ---------- Exception Handlers ----------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors: dict[str, dict[str, list[str]]] = {}

    for err in exc.errors():
        loc = err["loc"]
        # body or query
        source = str(loc[0]) if loc else "request"

        if err["type"] == "json_invalid":
            field = "root"
        else:
            field = ".".join(str(p) for p in loc[1:]) or "root"

        msg = err["msg"].removeprefix("Value error, ")
        errors.setdefault(source, {}).setdefault(field, []).append(msg)

    return JSONResponse(
        status_code=400,
        content={"detail": "Validation failed", "errors": errors},
    )


# ---------- Item Endpoints ----------


@app.get("/items", response_model=PaginatedItemsOut)
def list_items(
    category: Optional[str] = None,
    sort: Optional[str] = None,
    search: Optional[str] = Query(
        None,
        max_length=100,
        description="Case-insensitive search on item title and description",
    ),
    page: int = Query(1, ge=1, description="Page number, starting at 1"),
    page_size: int = Query(
        DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description=f"Items per page (max {MAX_PAGE_SIZE})",
    ),
):
    """Return all marketplace items, newest first."""
    return get_items_page(
        category=category,
        sort=sort,
        search=search,
        page=page,
        page_size=page_size,
    )


@app.get("/items/{item_id}", response_model=ItemOut)
def item_detail(item_id: int):
    """Return a single item by its id."""
    item = get_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/items/{item_id}/similar", response_model=list[ItemOut])
def similar_items(item_id: int):
    """Up to 5 newest items in the same category as `item_id`, excluding itself."""
    items = get_similar_items(item_id)
    if items is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return items

@app.post("/items", response_model=ItemOut, status_code=201)
def add_item(item: ItemCreate, current_seller: dict = Depends(get_current_user)):
    """Create a new marketplace listing."""
    return create_item(item, current_seller)

# ---------- Category Endpoints ----------

@app.get("/categories", response_model=list[CategoryOut])
def list_categories():
    """Return all item categories, most frequest first."""
    return get_all_categories()

# ---------- Search ----------

@app.get("/items/search")
def search_items(q: str = ""):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM items WHERE title LIKE '%{q}%' OR description LIKE '%{q}%' ORDER BY created_at DESC")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


# ---------- Admin ----------

@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM items ORDER BY created_at DESC")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    html = "<html><head><title>Admin - Items</title></head><body>"
    html += "<h1>Marketplace Admin Panel</h1>"
    for item in items:
        html += f"<div class='item'><h3>{item['title']}</h3><p>{item['description']}</p><span>Seller: {item['seller_name']}</span></div>"
    html += "</body></html>"
    return HTMLResponse(content=html)


# ---------- Delete item (owner only) ----------

@app.delete("/items/{item_id}", dependencies=[Depends(require_item_owner)])
def delete_item(item_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Item deleted"}



@app.patch("/items/{item_id}" , response_model=ItemOut, dependencies=[Depends(require_item_owner)])
def update_item_sold(item_id: int, payload: ItemSoldUpdate):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        # atomic: only touches the row if the state actually changes
        cursor.execute(
            "UPDATE items SET is_sold = %s WHERE id = %s AND NOT (is_sold <=> %s)",
            (payload.is_sold, item_id, payload.is_sold),
        )

        # if no rows were updated
        if cursor.rowcount == 0:
            conn.rollback()

            cursor.execute("SELECT id FROM items WHERE id = %s", (item_id,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Item not found")
            
            state = "sold" if payload.is_sold else "available"

            raise HTTPException(status_code=409, detail=f"Item is already {state}")

        cursor.execute("SELECT * FROM items WHERE id = %s", (item_id,))
        row = cursor.fetchone()
        conn.commit()
        return _serialize_row(row)

    except HTTPException:
        raise

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

# ---------- Auth Endpoints ----------

@app.post("/auth/register", response_model=SellerOut, status_code=201)
def register(data: RegisterRequest):
    try:
        return create_seller(
            username=data.username,
            password_hash=hash_password(data.password),
            display_name=data.display_name,
            email=data.email,
        )
    except UsernameTakenError:
        raise HTTPException(status_code=409, detail="Username already taken")

@app.post("/auth/login", response_model=TokenOut)
def login(data: LoginRequest):
    seller = get_seller_by_username(data.username)
    password_ok = verify_password(
        data.password,
        seller["password_hash"] if seller else DUMMY_HASH
    )

    if seller is None or not password_ok:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenOut(access_token=create_token(seller["id"]))

@app.get("/auth/me", response_model=SellerOut)
def me(current_seller: dict = Depends(get_current_user)):
    return current_seller