# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"hello":"world"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int,user_id: int):
#     return {"item_id": item_id,"user_id":user_id}
# -----------------------------------------------------
# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"hello": "world"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, user_id: int):
#     return {"item_id": item_id, "user_id": user_id}

# @app.post("/items/")
# def create_item(item_id: int, user_id: int):
#     return {"message": "Item created", "item_id": item_id, "user_id": user_id}
# -----------------------------------------------------------------------

import sqlite3
import os

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


# Create FastAPI application
app = FastAPI()

# Jinja2 templates folder
templates = Jinja2Templates(directory="templates")

# Database path
DATABASE = os.path.join(
    os.path.dirname(__file__),
    "todo.db"
)

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE)

    # Access columns by name
    conn.row_factory = sqlite3.Row

    return conn

def init_db():
    """Initialize database and create todos table."""
    conn = get_db_connection()

    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    conn.close()

# Initialize database when application starts
init_db()

# --------------------------------------------------
# READ - Display all tasks
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):

    conn = get_db_connection()

    todos = conn.execute(
        "SELECT * FROM todos ORDER BY id DESC"
    ).fetchall()

    total = len(todos)

    completed = sum(
        1 for todo in todos
        if todo["completed"] == 1
    )

    pending = total - completed

    conn.close()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "todos": todos,
            "total": total,
            "completed": completed,
            "pending": pending
        }
    )


# --------------------------------------------------
# CREATE - Add new task
# --------------------------------------------------

@app.post("/add")
async def add(
    title: str = Form(""),
    description: str = Form("")
):

    title = title.strip()
    description = description.strip()

    if not title:
        return RedirectResponse(
            url="/",
            status_code=303
        )

    conn = get_db_connection()

    with conn:
        conn.execute(
            """
            INSERT INTO todos
            (title, description, completed)
            VALUES (?, ?, 0)
            """,
            (title, description)
        )

    conn.close()

    return RedirectResponse(
        url="/",
        status_code=303
    )


# --------------------------------------------------
# UPDATE - Toggle task completion
# --------------------------------------------------

@app.get("/toggle/{id}")
async def toggle(id: int):

    conn = get_db_connection()

    todo = conn.execute(
        """
        SELECT completed
        FROM todos
        WHERE id = ?
        """,
        (id,)
    ).fetchone()

    if todo:

        new_status = (
            0 if todo["completed"] == 1 else 1
        )

        with conn:
            conn.execute(
                """
                UPDATE todos
                SET completed = ?
                WHERE id = ?
                """,
                (new_status, id)
            )

    conn.close()

    return RedirectResponse(
        url="/",
        status_code=303
    )


# --------------------------------------------------
# UPDATE - Show edit page
# --------------------------------------------------

@app.get("/edit/{id}", response_class=HTMLResponse)
async def edit_page(
    request: Request,
    id: int
):

    conn = get_db_connection()

    todo = conn.execute(
        """
        SELECT *
        FROM todos
        WHERE id = ?
        """,
        (id,)
    ).fetchone()

    conn.close()

    if not todo:
        return RedirectResponse(
            url="/",
            status_code=303
        )

    return templates.TemplateResponse(
        "edit.html",
        {
            "request": request,
            "todo": todo
        }
    )


# --------------------------------------------------
# UPDATE - Save edited task
# --------------------------------------------------

@app.post("/edit/{id}")
async def edit(
    id: int,
    title: str = Form(""),
    description: str = Form("")
):

    title = title.strip()
    description = description.strip()

    if not title:
        return RedirectResponse(
            url=f"/edit/{id}",
            status_code=303
        )

    conn = get_db_connection()

    with conn:
        conn.execute(
            """
            UPDATE todos
            SET title = ?, description = ?
            WHERE id = ?
            """,
            (title, description, id)
        )

    conn.close()

