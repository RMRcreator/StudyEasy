from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)
bcrypt = Bcrypt(app)

def get_db_connection():
    conn = sqlite3.connect("userdata.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS userdata (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO userdata (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return jsonify({"message": "Account created successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Username already exists"}), 409
    finally:
        conn.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM userdata WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()

    if user and bcrypt.check_password_hash(user[2], password):
        return jsonify({"message": "Login successful", "redirect": url_for('welcome')}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401


@app.route("/dashboard")
def welcome():
    return render_template("welcome.html")

if __name__ == "__main__":
    create_table()
    app.run(debug=True)
