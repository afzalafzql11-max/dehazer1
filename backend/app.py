from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import os
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

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
        email TEXT,
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

def dehaze_image(path):

    img = cv2.imread(path)

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l,a,b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0,tileGridSize=(8,8))
    cl = clahe.apply(l)

    limg = cv2.merge((cl,a,b))
    final = cv2.cvtColor(limg,cv2.COLOR_LAB2BGR)

    filename = os.path.basename(path)
    new_path = os.path.join(DEHAZE_FOLDER, filename)

    cv2.imwrite(new_path, final)

    return new_path

# ---------------- SIGNUP ----------------

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data["email"]
    password = data["password"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Check if user already exists
    existing = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"status":"fail","message":"User already exists"})

    c.execute("INSERT INTO users(email,password) VALUES (?,?)", (email,password))
    conn.commit()
    conn.close()

    return jsonify({"status":"success"})   # <-- MUST be exactly "success"

# ---------------- LOGIN ----------------

@app.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data["email"]
    password = data["password"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    user = c.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email,password)
    ).fetchone()

    conn.close()

    if user:
        return jsonify({"status":"success","user_id":user[0]})

    return jsonify({"status":"invalid login"})

# ---------------- UPLOAD & DEHAZE ----------------

@app.route("/dehaze", methods=["POST"])
def dehaze():

    user_id = request.form["user_id"]
    file = request.files["image"]

    path = os.path.join(UPLOAD_FOLDER,file.filename)

    file.save(path)

    new_path = dehaze_image(path)

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO history(user_id,image) VALUES (?,?)",
        (user_id,new_path)
    )

    conn.commit()
    conn.close()

    return send_file(new_path, as_attachment=True)

# ---------------- USER HISTORY ----------------

@app.route("/history/<user_id>")
def history(user_id):

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    data = c.execute(
        "SELECT image FROM history WHERE user_id=?",
        (user_id,)
    ).fetchall()

    conn.close()

    images = [i[0] for i in data]

    return jsonify(images)

# ---------------- DOWNLOAD ----------------

@app.route("/download")
def download():

    path = request.args.get("path")

    return send_file(path, as_attachment=True)

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run() 
