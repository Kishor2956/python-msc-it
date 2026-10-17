from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300), default="")
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    due_date = db.Column(db.Date, nullable=True)


def read_task_form():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "Medium")
    date_text = request.form.get("due_date", "").strip()

    if not title or len(title) > 150:
        raise ValueError("Title is required and must be at most 150 characters.")

    if len(description) > 300:
        raise ValueError("Description must be at most 300 characters.")

    if priority not in ("High", "Medium", "Low"):
        raise ValueError("Please select a valid priority.")

    due_date = None
    if date_text:
        try:
            due_date = datetime.strptime(date_text, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Please enter a valid due date.")

    return title, description, priority, due_date


@app.route("/")
def index():
    pending_tasks = Task.query.filter_by(
        is_completed=False
    ).order_by(Task.due_date.asc(), Task.id.desc()).all()

    completed_tasks = Task.query.filter_by(
        is_completed=True
    ).order_by(Task.id.desc()).all()

    return render_template(
        "index.html",
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
    )


@app.route("/add", methods=["POST"])
def add():
    try:
        title, description, priority, due_date = read_task_form()

        task = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )

        db.session.add(task)
        db.session.commit()
        flash("Task added successfully!", "success")

    except ValueError as error:
        flash(str(error), "error")

    return redirect(url_for("index"))


@app.route("/toggle/<int:id>")
def toggle(id):
    task = db.get_or_404(Task, id)
    task.is_completed = not task.is_completed
    db.session.commit()
    flash("Task status updated.", "success")
    return redirect(url_for("index"))


@app.route("/edit/<int:id>")
def edit(id):
    task = db.get_or_404(Task, id)
    return render_template("edit.html", task=task)


@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    task = db.get_or_404(Task, id)

    try:
        title, description, priority, due_date = read_task_form()

        task.title = title
        task.description = description
        task.priority = priority
        task.due_date = due_date

        db.session.commit()
        flash("Task updated successfully!", "success")
        return redirect(url_for("index"))

    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for("edit", id=id))


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    task = db.get_or_404(Task, id)
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted successfully.", "success")
    return redirect(url_for("index"))


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
