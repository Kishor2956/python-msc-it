import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'supersecretkey_for_todo_app'

DATABASE = os.path.join(os.path.dirname(__file__), 'todo.db')

def get_db_connection():
    """Create and return a database connection with row access by column name."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database and create the todos table if it doesn't exist."""
    conn = get_db_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    conn.close()

# Auto-initialize database on start
init_db()

@app.route('/')
def index():
    """READ: Display all tasks and stats."""
    conn = get_db_connection()
    todos = conn.execute('SELECT * FROM todos ORDER BY id DESC').fetchall()
    
    total = len(todos)
    completed = sum(1 for todo in todos if todo['completed'] == 1)
    pending = total - completed
    
    conn.close()
    return render_template('index.html', todos=todos, total=total, completed=completed, pending=pending)

@app.route('/add', methods=['POST'])
def add():
    """CREATE: Add a new task."""
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()

    if not title:
        flash('Task title is required!', 'error')
        return redirect(url_for('index'))

    conn = get_db_connection()
    with conn:
        conn.execute(
            'INSERT INTO todos (title, description, completed) VALUES (?, ?, 0)',
            (title, description)
        )
    conn.close()
    flash('Task added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/toggle/<int:id>')
def toggle(id):
    """UPDATE: Toggle task completion status."""
    conn = get_db_connection()
    todo = conn.execute('SELECT completed FROM todos WHERE id = ?', (id,)).fetchone()
    if todo:
        new_status = 0 if todo['completed'] == 1 else 1
        with conn:
            conn.execute('UPDATE todos SET completed = ? WHERE id = ?', (new_status, id))
        status_text = 'completed' if new_status == 1 else 'marked pending'
        flash(f'Task #{id} {status_text}!', 'info')
    else:
        flash('Task not found!', 'error')
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """UPDATE: Edit task title and description."""
    conn = get_db_connection()
    todo = conn.execute('SELECT * FROM todos WHERE id = ?', (id,)).fetchone()

    if not todo:
        conn.close()
        flash('Task not found!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        if not title:
            flash('Task title cannot be empty!', 'error')
            conn.close()
            return render_template('edit.html', todo=todo)

        with conn:
            conn.execute(
                'UPDATE todos SET title = ?, description = ? WHERE id = ?',
                (title, description, id)
            )
        conn.close()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', todo=todo)

@app.route('/delete/<int:id>')
def delete(id):
    """DELETE: Remove a task by ID."""
    conn = get_db_connection()
    with conn:
        conn.execute('DELETE FROM todos WHERE id = ?', (id,))
    conn.close()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
