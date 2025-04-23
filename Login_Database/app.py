from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret'
bcrypt = Bcrypt(app)

def get_db_connection():
    conn = sqlite3.connect("userdata.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_notes_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def create_table():
    create_notes_table()
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
        session["user"] = username  # Set the user in the session
        return jsonify({"message": "Login successful", "redirect": url_for('welcome')}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401


@app.route("/dashboard")
def welcome():
    return render_template("welcome.html")
    
@app.route("/create_quiz")
def create_quiz():
    return render_template("create_quiz.html")

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    title = request.form.get('quiz_title')
    if not title:
        return "Quiz title is required", 400
    
    quiz = [];
    i = 1
    while True:
        q = request.form.get(f'question{i}')
        a = request.form.get(f'answer{i}')
        if not q or not a:
            break
        quiz.append((q,a))
        i += 1

    if 'quizzes' not in session:
        session['quizzes'] = {}

    quizzes = session['quizzes']
    quizzes[title] = quiz
    session['quizzes'] = quizzes
    #session['quiz_data'] = quiz
    return render_template("quiz_summary.html", quiz=quiz)

@app.route('/start_quiz/<title>')
def start_quiz(title):
    quizzes = session.get('quizzes', {})
    quiz = quizzes.get(title)
    if not quiz:
        return "Quiz not found", 404

    session['quiz_data'] = quiz
    session['quiz_index'] = 0
    session['quiz_score'] = 0
    return render_template('take_quiz.html', question=quiz[0][0], total=len(quiz), current=1)


@app.route('/take_quiz', methods=['GET'])
def take_quiz():
    quiz = session.get('quiz_data')
    if not quiz:
        return redirect(url_for('create_quiz'))
    session['quiz_index'] = 0
    session['quiz_score'] = 0
    return render_template('take_quiz.html', question=quiz[0][0], total=len(quiz), current=1)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    user_answer = request.form.get('user_answer', '').strip().lower()
    quiz = session.get('quiz_data', [])
    index = session.get('quiz_index', 0)

    if index >= len(quiz):
        return redirect(url_for('dashboard'))

    correct_answer = quiz[index][1].strip().lower()
    is_correct = user_answer == correct_answer
    session['quiz_score'] += int(is_correct)
    session['quiz_index'] += 1

    if session['quiz_index'] < len(quiz):
        next_question = quiz[session['quiz_index']][0]
        return render_template(
            'take_quiz.html',
            question=next_question,
            total=len(quiz),
            current=session['quiz_index'] + 1,
            feedback="Correct!" if is_correct else f"Incorrect. The correct answer was: {correct_answer}"
        )
    else:
        return render_template('take_quiz.html', completed=True, score=session['quiz_score'], total=len(quiz))
    

@app.route('/select_quiz')
def select_quiz():
    quizzes = session.get('quizzes', {})
    return render_template('select_quiz.html', quizzes=quizzes)

@app.route('/delete_quiz/<title>', methods=['POST'])
def delete_quiz(title):
    quizzes = session.get('quizzes', {})
    if title in quizzes:
        del quizzes[title]
        session['quizzes'] = quizzes
    return redirect(url_for('select_quiz'))

@app.route("/notes", methods=["GET", "POST"])
def notes():
    if "user" not in session:
        return redirect(url_for("home"))
    
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        cur.execute("INSERT INTO notes (username, title, content) VALUES (?, ?, ?)",
                    (session["user"], title, content))
        conn.commit()

    cur.execute("SELECT * FROM notes WHERE username = ?", (session["user"],))
    user_notes = cur.fetchall()
    conn.close()
    return render_template("notes.html", notes=user_notes)

if __name__ == "__main__":
    create_table()
    create_notes_table()
    app.run(debug=True)