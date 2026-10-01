"""
Student Marketplace — FastAPI backend.

Run with:
    uvicorn app:app --reload --port 5000
"""

import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from typing import Optional
import html as html_lib

from database import init_db, get_db
from models import (
    ItemCreate, 
    ItemOut, 
    CategoryOut,
    _serialize_row, 
    get_all_items, 
    get_item_by_id, 
    create_item, 
    get_all_categories,
    ItemSoldUpdate
)

SECRET_KEY = "super-secret-key-123"

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


@app.get("/items", response_model=list[ItemOut])
def list_items(category: Optional[str] = None, sort: Optional[str] = None):
    """Return all marketplace items, newest first."""
    return get_all_items(category, sort)


@app.get("/items/{item_id}", response_model=ItemOut)
def item_detail(item_id: int):
    """Return a single item by its id."""
    item = get_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/items", response_model=ItemOut, status_code=201)
def add_item(item: ItemCreate):
    """Create a new marketplace listing."""
    return create_item(item)

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
    cursor.execute(f"SELECT * FROM items WHERE title LIKE %s OR description LIKE %s ORDER BY created_at DESC", (f"%{q}%", f"%{q}%"))
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
        title = html_lib.escape(item['title'])
        description = html_lib.escape(item['description'] or "")
        seller = html_lib.escape(item['seller_name'])
        html += f"<div class='item'><h3>{title}</h3><p>{description}</p><span>Seller: {seller}</span></div>"

    return HTMLResponse(content=html)


# ---------- Delete item (no auth) ----------

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Item deleted"}



@app.patch("/items/{item_id}" , response_model=ItemOut)
def update_item_sold(item_id: int, payload: ItemSoldUpdate):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("UPDATE items SET is_sold = %s WHERE id = %s", (payload.is_sold, item_id))
    conn.commit()
    cursor.execute("SELECT * FROM items WHERE id = %s", (item_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return _serialize_row(row)


  


@app.post("/sellers/register")
def register_seller(data: dict):
    name = data.get("name", "")
    email = data.get("email", "")
    logging.info(f"New seller registered: {name} ({email})")
    return {"message": f"Seller {name} registered"}
