from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import sqlite3
import os
import cv2
import numpy as np
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
DEHAZE_FOLDER = "dehazed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DEHAZE_FOLDER, exist_ok=True)

# -------- DATABASE --------

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

# -------- HOME PAGE --------

@app.route("/")
def home():
    return render_template("index.html")

# -------- DEHAZE FUNCTION --------

def dehaze_image(path):

    img = cv2.imread(path)

    h, w = img.shape[:2]
    if w > 1200:
        scale = 1200 / w
        img = cv2.resize(img,(int(w*scale),int(h*scale)))

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l,a,b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
    l = clahe.apply(l)

    lab = cv2.merge((l,a,b))
    result = cv2.cvtColor(lab,cv2.COLOR_LAB2BGR)

    filename = os.path.basename(path)
    new_path = os.path.join(DEHAZE_FOLDER,filename)

    cv2.imwrite(new_path,result,[cv2.IMWRITE_JPEG_QUALITY,90])

    return new_path

# -------- SIGNUP --------

@app.route("/signup",methods=["POST"])
def signup():

    data=request.json

    conn=sqlite3.connect("database.db")
    c=conn.cursor()

    c.execute("INSERT INTO users(email,password) VALUES (?,?)",
    (data["email"],data["password"]))

    conn.commit()
    conn.close()

    return jsonify({"status":"signup success"})

# -------- LOGIN --------

@app.route("/login",methods=["POST"])
def login():

    data=request.json

    conn=sqlite3.connect("database.db")
    c=conn.cursor()

    user=c.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (data["email"],data["password"])
    ).fetchone()

    conn.close()

    if user:
        return jsonify({"status":"success","user_id":user[0]})

    return jsonify({"status":"invalid"})

# -------- UPLOAD IMAGE --------

@app.route("/dehaze",methods=["POST"])
def dehaze():

    user_id=request.form["user_id"]
    file=request.files["image"]

    filename=str(uuid.uuid4())+".jpg"

    path=os.path.join(UPLOAD_FOLDER,filename)
    file.save(path)

    new_path=dehaze_image(path)

    conn=sqlite3.connect("database.db")
    c=conn.cursor()

    c.execute(
        "INSERT INTO history(user_id,image) VALUES (?,?)",
        (user_id,new_path)
    )

    conn.commit()
    conn.close()

    return send_file(
        new_path,
        mimetype="image/jpeg",
        as_attachment=True,
        download_name="dehazed.jpg"
    )

# -------- HISTORY --------

@app.route("/history/<user_id>")
def history(user_id):

    conn=sqlite3.connect("database.db")
    c=conn.cursor()

    data=c.execute(
        "SELECT image FROM history WHERE user_id=?",
        (user_id,)
    ).fetchall()

    conn.close()

    images=[i[0] for i in data]

    return jsonify(images)

# -------- DOWNLOAD --------

@app.route("/download")
def download():

    path=request.args.get("path")

    if not os.path.exists(path):
        return jsonify({"error":"file not found"})

    return send_file(path,as_attachment=True)

if __name__ == "__main__":
    app.run()
