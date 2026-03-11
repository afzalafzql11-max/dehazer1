// =========================
// API Base URL
// =========================
const API = "https://dehazer1.onrender.com";

// =========================
// Global user session
// =========================
let user_id = null;

// =========================
// Helper Functions
// =========================

// Show alerts
function showAlert(message) {
    alert(message);
}

// Set user session
function setUserSession(id) {
    user_id = id;
    localStorage.setItem("user_id", id);
}

// Get saved user session
function getUserSession() {
    return localStorage.getItem("user_id");
}

// =========================
// SIGNUP
// =========================
async function signup() {
    const email = document.getElementById("signup_email").value;
    const password = document.getElementById("signup_pass").value;

    if (!email || !password) {
        showAlert("Email and password cannot be empty.");
        return;
    }

    try {
        const res = await fetch(`${API}/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();

        if (data.success) {
            showAlert("Signup successful. You can now login!");
        } else {
            showAlert(data.message || "Signup failed.");
        }
    } catch (err) {
        showAlert("Error connecting to server.");
        console.error(err);
    }
}

// =========================
// LOGIN
// =========================
async function login() {
    const email = document.getElementById("login_email").value;
    const password = document.getElementById("login_pass").value;

    if (!email || !password) {
        showAlert("Email and password cannot be empty.");
        return;
    }

    try {
        const res = await fetch(`${API}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (data.success) {
            setUserSession(data.user_id);
            showAlert("Login successful!");
            loadHistory();
        } else {
            showAlert(data.message || "Login failed.");
        }
    } catch (err) {
        showAlert("Error connecting to server.");
        console.error(err);
    }
}

// =========================
// UPLOAD & DEHAZE IMAGE
// =========================
async function uploadImage() {
    if (!user_id) {
        showAlert("Please login first.");
        return;
    }

    const fileInput = document.getElementById("image_file");
    if (fileInput.files.length === 0) {
        showAlert("Please select an image.");
        return;
    }

    const formData = new FormData();
    formData.append("image", fileInput.files[0]);
    formData.append("user_id", user_id);

    try {
        const res = await fetch(`${API}/dehaze`, {
            method: "POST",
            body: formData
        });

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);

        document.getElementById("dehazed_image").src = url;
        addToHistory(url); // optional: update frontend history
        showAlert("Image dehazed! You can download it now.");
    } catch (err) {
        showAlert("Failed to dehaze image.");
        console.error(err);
    }
}

// =========================
// DOWNLOAD IMAGE
// =========================
function downloadImage(imgSrc, filename = "dehazed.png") {
    const a = document.createElement("a");
    a.href = imgSrc;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// =========================
// VIEW HISTORY
// =========================
async function loadHistory() {
    if (!user_id) return;

    try {
        const res = await fetch(`${API}/history/${user_id}`);
        const data = await res.json();

        const historyContainer = document.getElementById("history");
        historyContainer.innerHTML = "";

        if (data.success && data.images.length > 0) {
            data.images.forEach(imgUrl => {
                const img = document.createElement("img");
                img.src = imgUrl;
                img.width = 150;
                img.height = 150;
                img.style.margin = "10px";
                img.style.cursor = "pointer";
                img.onclick = () => downloadImage(imgUrl);
                historyContainer.appendChild(img);
            });
        } else {
            historyContainer.innerHTML = "<p>No history yet.</p>";
        }
    } catch (err) {
        console.error(err);
    }
}

// =========================
// LOGOUT
// =========================
function logout() {
    user_id = null;
    localStorage.removeItem("user_id");
    showAlert("Logged out successfully.");
    document.getElementById("dehazed_image").src = "";
    document.getElementById("history").innerHTML = "";
}

// =========================
// INIT
// =========================
window.onload = () => {
    const savedUser = getUserSession();
    if (savedUser) {
        user_id = savedUser;
        loadHistory();
    }
};
