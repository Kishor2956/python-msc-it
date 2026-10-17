from flask import Flask, render_template, request
from db_config import db, TODO

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
def root():
    return "<h1>hello welcom to Flask</h1>"


@app.route("/home", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        name = request.form.get("todo-name")
        date = request.form.get("todo-date")
        status = request.form.get("todo-status")

        
        todo = TODO(
            name=name,
            due_date=date,
            status=status
        )

    
        db.session.add(todo)
        db.session.commit()

        return "Data Stored Successfully!" 

    return render_template("index.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
