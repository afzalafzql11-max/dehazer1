from flask import Flask, request, redirect, session, send_file, render_template_string
import sqlite3
import os
import cv2

app = Flask(__name__)
app.secret_key = "secret"

UPLOAD_FOLDER = "uploads"
DEHAZE_FOLDER = "dehazed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DEHAZE_FOLDER, exist_ok=True)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- DEHAZE FUNCTION ----------------
def dehaze(path):
    img = cv2.imread(path)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    name = os.path.basename(path)
    new_path = os.path.join(DEHAZE_FOLDER, name)
    cv2.imwrite(new_path, final)
    return new_path

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            return "Email and password required"
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        existing = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if existing:
            conn.close()
            return "Email already exists"
        c.execute("INSERT INTO users(email,password) VALUES (?,?)", (email,password))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template_string("""
    <h2>Signup</h2>
    <form method="POST">
        <input name="email" placeholder="Email"><br><br>
        <input name="password" type="password" placeholder="Password"><br><br>
        <button>Signup</button>
    </form>
    <br>
    <a href="/login">Login</a>
    """)

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        user = c.execute("SELECT * FROM users WHERE email=? AND password=?", (email,password)).fetchone()
        conn.close()
        if user:
            session["user"] = user[0]
            return redirect("/dashboard")
        return "Invalid credentials"
    return render_template_string("""
    <h2>Login</h2>
    <form method="POST">
        <input name="email" placeholder="Email"><br><br>
        <input name="password" type="password" placeholder="Password"><br><br>
        <button>Login</button>
    </form>
    <br>
    <a href="/signup">Signup</a>
    """)

# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")
    if request.method == "POST":
        if "image" not in request.files:
            return "No image selected"
        file = request.files["image"]
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        new_path = dehaze(path)
        # save to history
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO history(user_id,image) VALUES (?,?)", (session["user"], new_path))
        conn.commit()
        conn.close()
        return send_file(new_path, as_attachment=True)
    return render_template_string("""
    <h2>Image Dehazer</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="image"><br><br>
        <button>Dehaze Image</button>
    </form>
    <br>
    <a href="/history">View History</a><br><br>
    <a href="/logout">Logout</a>
    """)

# ---------------- HISTORY ----------------
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    data = c.execute("SELECT image FROM history WHERE user_id=?", (session["user"],)).fetchall()
    conn.close()
    html = "<h2>Your Dehazed Images</h2>"
    for img in data:
        html += f'<a href="/download?path={img[0]}">Download Image</a><br><br>'
    html += '<br><a href="/dashboard">Back</a>'
    return html

# ---------------- DOWNLOAD ----------------
@app.route("/download")
def download():
    path = request.args.get("path")
    if not path or not os.path.exists(path):
        return "File not found"
    return send_file(path, as_attachment=True)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- RUN ----------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
