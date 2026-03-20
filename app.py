from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "secret_key"


def init_db():
    with sqlite3.connect("demoex.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        is_admin INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS applications(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        course_name TEXT,
                        start_date TEXT,
                        payment_method TEXT,
                        status TEXT DEFAULT 'На рассмотрении')''')
        conn.commit()
init_db()


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])

def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect("demoex.db") as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
                conn.commit()
                return redirect('/login')
            except:
                return "Пользователь уже существует"
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect("demoex.db") as conn:  # ✅ исправлено
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['is_admin'] = user[3]
                return redirect('/dashboard')
            else:
                return "Неверный логин или пароль"
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    if session['is_admin']:
        return redirect('/admin')
    with sqlite3.connect("demoex.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM applications WHERE user_id=?", (session['user_id'],))
        apps = c.fetchall()
    return render_template('dashboard.html', apps=apps)


@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        course = request.form['course']
        start_date = request.form['start_date']
        payment = request.form['payment']
        with sqlite3.connect("demoex.db") as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO applications(user_id, course_name, start_date, payment_method)
                         VALUES(?,?,?,?)''', (session['user_id'], course, start_date, payment))
            conn.commit()
        return redirect('/dashboard')
    return render_template('apply.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user_id' not in session or not session['is_admin']:
        return redirect('/')
    with sqlite3.connect("demoex.db") as conn:
        c = conn.cursor()
        if request.method == 'POST':
            app_id = request.form['app_id']
            status = request.form['status']
            c.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
            conn.commit()
        c.execute('''SELECT applications.id, users.username, course_name, start_date, payment_method, status
                     FROM applications JOIN users ON users.id = applications.user_id''')
        apps = c.fetchall()
    return render_template('admin.html', apps=apps)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
