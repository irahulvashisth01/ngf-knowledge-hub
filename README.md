# 📚 NotesHub

🚀 **Modern Notes Sharing Platform for B.Tech Students**

🌐 **Live Website:** https://btechnotes.online
⚙️ **Deployment:** https://notes-hub-lpxg.onrender.com

---

## 🏆 Overview

**NotesHub** is a full-stack web application designed to help engineering students **access, upload, and manage academic notes** in a structured, semester-wise format.

It provides a **clean, responsive UI, authentication system, admin dashboard, blog-ready structure, and cloud deployment**, making it a **portfolio-ready + real-world SaaS project**.

---

## ✨ Features

### 👨‍🎓 User Features

* 📚 Browse notes without login
* 🔍 Search notes by subject
* 👁 View notes directly in browser
* ⬇ Download notes
* 📱 Fully responsive (Mobile + Desktop)
* 📂 Semester-wise structured navigation

---

### 🔐 Authentication System

* User Registration (Name, Email, Mobile)
* Secure Login (Session-based)
* Role-based access (Admin / User)
* Smart redirects

---

### 🧑‍💼 Admin Panel

* 📤 Approve / Reject notes
* 🗑 Delete notes
* 👥 Manage users (Admin ↔ User)
* 📊 Dashboard-style UI

---

### 📊 Advanced Features

* 📈 Download tracking system
* 🏆 Top downloaded notes section
* 🔎 Backend filtering
* 🎯 Clean SaaS-style UI

---

### 📱 Responsive Design

* 💻 Desktop → Professional dashboard UI
* 📱 Mobile → App-style interface (bottom navigation)

---

### ⚖️ Legal Pages (AdSense Ready)

* 📄 Privacy Policy
* 📄 Terms & Conditions
* 📄 Disclaimer
* 📄 About Us
* 📄 Contact Page

---

## 🛠️ Tech Stack

| Category  | Technology            |
| --------- | --------------------- |
| Backend   | Python                |
| Framework | Flask                 |
| Database  | SQLite                |
| Frontend  | HTML, CSS, JavaScript |
| Server    | Gunicorn              |
| Hosting   | Render                |
| Domain    | GoDaddy               |
| PWA       | Service Workers       |

---

## 📂 Project Structure

```
NotesHub/
│── app.py
│── config.py
│── db.sqlite3
│── requirements.txt
│── runtime.txt
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── btech.html
│   ├── semester.html
│   ├── subjects.html
│   ├── notes.html
│   ├── upload.html
│   ├── admin.html
│   ├── about.html
│   ├── contact.html
│   ├── privacy.html
│   ├── terms.html
│   └── disclaimer.html
│
├── static/
│   ├── images/
│   ├── icons/
│   └── js/
│
└── uploads/
```

---

## ⚙️ Installation (Local Setup)

### 1️⃣ Clone Repository

```bash
git clone https://github.com/irahulvashisth01/Notes-Hub.git
cd NotesHub
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Run Server

```bash
python app.py
```

---

### 4️⃣ Open in Browser

```
http://127.0.0.1:10000
```

---

## 🌐 Deployment

### 🚀 Render Deployment

* Hosted on Render
* Uses Gunicorn for production

### 🔗 Custom Domain

* Domain connected via GoDaddy
* 🌍 https://btechnotes.online

---

## ⚠️ Storage Limitation (Important)

Currently:

* Files uploaded locally are stored in `/uploads`

### 🚨 Issue:

* Local server ≠ deployed server storage

### ✅ Recommended Solution:

* Use **Cloud Storage**:

  * ☁️ Cloudinary
  * ☁️ AWS S3
  * ☁️ Render Persistent Disk

---

## 🔒 Access Control

| Feature        | Access Level   |
| -------------- | -------------- |
| Browse Notes   | Public         |
| View Notes     | Login Required |
| Download Notes | Login Required |
| Upload Notes   | Login Required |
| Admin Panel    | Admin Only     |

---

## 📈 Future Enhancements

* 🔔 Push Notifications
* ⭐ Bookmark Notes
* ☁️ Cloud Storage Integration
* 🧠 AI Note Recommendations
* 📊 Analytics Dashboard
* 🔍 Advanced Search System
* 🗄 PostgreSQL Migration

---

## 👨‍💻 Developer

**Rahul Vashisth**
🎓 B.Tech Engineering Student

📧 Email: [rahulvashistha97@gmail.com](mailto:rahulvashistha97@gmail.com)
📞 Phone: +91 7056212054

🔗 Instagram: https://www.instagram.com/irahulvashisth
🔗 LinkedIn: https://www.linkedin.com/in/rahul-sharma-753879352

---

## ⭐ Support & Contribution

If you like this project:

* ⭐ Star this repository
* 🔁 Share with others
* 💡 Contribute improvements

---

## 🚀 Final Note

This project demonstrates:

* Full-stack web development
* Authentication & authorization
* Admin dashboard system
* Responsive SaaS UI design
* Cloud deployment
* AdSense-ready structure

💯 **Portfolio Ready | Production Ready | Monetization Ready**

---
