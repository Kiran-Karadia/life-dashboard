import datetime
from flask import Flask, abort, render_template
from markupsafe import escape

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def hello():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/capitalise/<word>")
def capitalise(word: str):
    return escape(word).upper()

@app.route("/add/<int:n1>/<int:n2>")
def sum(n1, n2):
    return f"When you add {n1} and {n2}, you get {n1 + n2}"

@app.route("/users/<int:user_id>")
def greet_user(user_id):
    all_users = ["Kiran", "Lucy", "Vince", "Leo"]
    try:
        return "<h2>{}</h2>".format(f"Hi there {all_users[user_id]}!")
    except Exception as error:
        abort(404, error)

@app.route("/time")
def time():
    return render_template("index.html", utc_dt=(datetime.datetime.now()))

@app.route("/comments")
def comments():
    comments = [
        "First",
        "Second",
        "Third",
        "Fourth",
        "Fifth"
    ]
    return render_template("comments.html", comments=comments)