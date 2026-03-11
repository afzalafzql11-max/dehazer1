from flask import Flask, request, jsonify, send_file
import sqlite3
import os
import cv2

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# DATABASE
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        password TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        image TEXT)""")

    conn.commit()
    conn.close()

init_db()


# DEHAZE
def dehaze_image(path):

    img = cv2.imread(path)

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l,a,b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0,tileGridSize=(8,8))
    cl = clahe.apply(l)

    limg = cv2.merge((cl,a,b))
    final = cv2.cvtColor(limg,cv2.COLOR_LAB2BGR)

    new_path = path.replace("uploads","uploads/dehazed")
    os.makedirs("uploads/dehazed",exist_ok=True)

    cv2.imwrite(new_path,final)

    return new_path


# SIGNUP
@app.route("/signup", methods=["POST"])
def signup():

    data = request.json

    email = data["email"]
    password = data["password"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("INSERT INTO users(email,password) VALUES (?,?)",(email,password))
    conn.commit()

    user_id = c.lastrowid

    conn.close()

    return jsonify({"status":"success","user_id":user_id})


# LOGIN
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
        return jsonify({
            "status":"success",
            "user_id":user[0]
        })

    return jsonify({"status":"fail"})


# DEHAZE UPLOAD
@app.route("/dehaze", methods=["POST"])
def dehaze():

    user_id = request.form["user_id"]
    file = request.files["image"]

    path = os.path.join(UPLOAD_FOLDER,file.filename)
    file.save(path)

    new_path = dehaze_image(path)

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("INSERT INTO history(user_id,image) VALUES (?,?)",(user_id,new_path))
    conn.commit()
    conn.close()

    return send_file(new_path, as_attachment=True)


# HISTORY
@app.route("/history/<user_id>")
def history(user_id):

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    data = c.execute(
        "SELECT image FROM history WHERE user_id=?",
        (user_id,)
    ).fetchall()

    conn.close()

    images = [x[0] for x in data]

    return jsonify(images)


# DOWNLOAD
@app.route("/download")
def download():

    path = request.args.get("path")

    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run()
