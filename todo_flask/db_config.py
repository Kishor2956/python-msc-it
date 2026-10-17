from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TODO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(100), nullable=False)
