
from datetime import date
from hashlib import pbkdf2_hmac, sha256
from secrets import token_hex

from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import (
    create_engine, Column, Integer, String,
    Boolean, Date, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(title="Todo Manager")

app.add_middleware(
    SessionMiddleware,
    secret_key=token_hex(32),
    same_site="lax",
    https_only=False
)

templates = Jinja2Templates(directory="templates")

engine = create_engine(
    "sqlite:///./todo.db",
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(300), nullable=False)

    tasks = relationship(
        "Todoapp", back_populates="user",
        cascade="all, delete-orphan"
    )


class Todoapp(Base):
    __tablename__ = "todoapp"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), default="")
    priority = Column(String(50), default="Medium")
    is_completed = Column(Boolean, default=False)
    due_date = Column(Date, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="tasks")


Base.metadata.create_all(bind=engine)


def hash_password(password: str) -> str:
    salt = token_hex(16)
    digest = pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 200_000
    ).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, expected = stored.split("$", 1)
        actual = pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 200_000
        ).hex()
        return actual == expected
    except (ValueError, TypeError):
        # Supports login with accounts created by the old plain-text code.
        return stored == password


def current_user(request: Request, db):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def page(request, name, **context):
    return templates.TemplateResponse(
        request=request,
        name=name,
        context=context
    )


def go(path):
    return RedirectResponse(path, status_code=303)


def parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Date must be in YYYY-MM-DD format"
        )


def owned_task(db, task_id, user_id):
    task = db.query(Todoapp).filter(
        Todoapp.id == task_id,
        Todoapp.user_id == user_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/")
def home(request: Request):
    if request.session.get("user_id"):
        return go("/dashboard")
    return page(request, "home.html")


@app.get("/register")
def register_page(request: Request):
    if request.session.get("user_id"):
        return go("/dashboard")
    return page(request, "register.html", error=None)


@app.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    name, email = name.strip(), email.strip().lower()
    if not name or len(password) < 8:
        return page(
            request, "register.html",
            error="Enter your name and a password of at least 8 characters."
        )

    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            return page(
                request, "register.html",
                error="Email already registered."
            )
        user = User(
            name=name, email=email,
            password=hash_password(password)
        )
        db.add(user)
        db.commit()
        return go("/login")
    finally:
        db.close()


@app.get("/login")
def login_page(request: Request):
    return page(request, "login.html", error=None)


@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            User.email == email.strip().lower()
        ).first()
        if not user or not verify_password(password, user.password):
            return page(
                request, "login.html",
                error="Invalid email or password."
            )
        # Upgrade an old plain-text password on successful login.
        if "$" not in user.password:
            user.password = hash_password(password)
            db.commit()

        request.session.clear()
        request.session["user_id"] = user.id
        return go("/dashboard")
    finally:
        db.close()


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return go("/")


@app.get("/dashboard")
def dashboard(request: Request):
    db = SessionLocal()
    try:
        user = current_user(request, db)
        if not user:
            return go("/login")
        tasks = db.query(Todoapp).filter(
            Todoapp.user_id == user.id
        ).order_by(Todoapp.id.desc()).all()
        return page(
            request, "dashboard.html",
            user=user, tasks=tasks,
            total=len(tasks),
            pending=sum(not t.is_completed for t in tasks),
            completed=sum(t.is_completed for t in tasks)
        )
    finally:
        db.close()


@app.get("/tasks/add")
def add_task_page(request: Request):
    if not request.session.get("user_id"):
        return go("/login")
    return page(request, "add_task.html", error=None)


@app.post("/tasks")
def add_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("Medium"),
    due_date: str = Form("")
):
    db = SessionLocal()
    try:
        user = current_user(request, db)
        if not user:
            return go("/login")
        title = title.strip()
        if not title:
            return page(
                request, "add_task.html",
                error="Task title is required."
            )
        task = Todoapp(
            title=title,
            description=description.strip(),
            priority=priority if priority in ["Low", "Medium", "High"] else "Medium",
            due_date=parse_date(due_date),
            user_id=user.id
        )
        db.add(task)
        db.commit()
        return go("/dashboard")
    finally:
        db.close()


@app.get("/tasks/{task_id}/edit")
def edit_task_page(request: Request, task_id: int):
    db = SessionLocal()
    try:
        user = current_user(request, db)
        if not user:
            return go("/login")
        task = owned_task(db, task_id, user.id)
        return page(
            request, "edit_task.html", task=task, error=None
        )
    finally:
        db.close()


@app.post("/tasks/{task_id}/edit")
def edit_task(
    request: Request,
    task_id: int,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("Medium"),
    due_date: str = Form("")
):
    db = SessionLocal()
    try:
        user = current_user(request, db)
        if not user:
            return go("/login")
        task = owned_task(db, task_id, user.id)
        title = title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="Title is required")
        task.title = title
        task.description = description.strip()
        task.priority = priority if priority in ["Low", "Medium", "High"] else "Medium"
        task.due_date = parse_date(due_date)
        db.commit()
        return go("/dashboard")
    finally:
        db.close()


@app.post("/tasks/{task_id}/toggle")
def toggle_task(request: Request, task_id: int):
    db = SessionLocal()
    try:
        user = current_user(request, db)
        if not user:
            return go("/login")
        task = owned_task(db, task_id, user.id)
        task.is_completed = not task.is_completed
        db.commit()
        return go("/dashboard")
    finally:
        db.close()


@app.post("/tasks/{task_id}/delete")
def delete_task(request: Request, task_id: int):
    db = SessionLocal()
    try:
        user = current_user(request, db)
        if not user:
            return go("/login")
        task = owned_task(db, task_id, user.id)
        db.delete(task)
        db.commit()
        return go("/dashboard")
    finally:
        db.close()


@app.get("/tasks/pending")
def pending_tasks(request: Request):
    db = SessionLocal()
    try:
        user = current_user(request, db)
        if not user:
            return go("/login")
        tasks = db.query(Todoapp).filter(
            Todoapp.user_id == user.id,
            Todoapp.is_completed.is_(False)
        ).order_by(Todoapp.id.desc()).all()
        return page(request, "pending.html", tasks=tasks)
    finally:
        db.close()


@app.get("/tasks/completed")
def completed_tasks(request: Request):
    db = SessionLocal()
    try:
        user = current_user(request, db)
        if not user:
            return go("/login")
        tasks = db.query(Todoapp).filter(
            Todoapp.user_id == user.id,
            Todoapp.is_completed.is_(True)
        ).order_by(Todoapp.id.desc()).all()
        return page(request, "completed.html", tasks=tasks)
    finally:
        db.close()


@app.get("/profile")
def profile_page(request: Request):
    db = SessionLocal()
    try:
        user = current_user(request, db)
        if not user:
            return go("/login")
        return page(request, "profile.html", user=user, error=None)
    finally:
        db.close()


@app.post("/profile")
def update_profile(
    request: Request,
    name: str = Form(...),
    email: str = Form(...)
):
    db = SessionLocal()
    try:
        user = current_user(request, db)
        if not user:
            return go("/login")

        name, email = name.strip(), email.strip().lower()
        if not name or not email:
            return page(
                request, "profile.html",
                user=user, error="Name and email are required."
            )
        other = db.query(User).filter(
            User.email == email, User.id != user.id
        ).first()
        if other:
            return page(
                request, "profile.html",
                user=user, error="That email is already in use."
            )
        user.name, user.email = name, email
        db.commit()
        return go("/profile")
    finally:
        db.close()


@app.get("/tasks/{task_id}")
def task_details(request: Request, task_id: int):
    db = SessionLocal()
    try:
        user = current_user(request, db)
        if not user:
            return go("/login")
        task = owned_task(db, task_id, user.id)
        return page(request, "task_details.html", task=task)
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
