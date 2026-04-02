# 📚 NotesHub

### 🚀 Modern Notes Sharing Platform for B.Tech Students

🌐 **Live Website:** https://btechnotes.online
⚙️ **Deployment:** https://notes-hub-lpxg.onrender.com

---

## 🏆 Overview

**NotesHub** is a full-stack web application designed for engineering students to **browse, upload, and download academic notes** in a structured, semester-wise format.

It features a clean UI, secure authentication system, admin control panel, and real-world cloud deployment with a custom domain.

---

## ✨ Key Features

### 👨‍🎓 User Features

* 📚 Browse notes without login
* 🔍 Search notes by subject or title
* 👁 View notes directly in browser (PDF preview)
* ⬇ Download notes *(login required)*
* 📱 Install as a Progressive Web App (PWA)

---

### 🔐 Authentication System

* User Registration (Name, Email, Mobile)
* Secure Login (Session-based)
* Smart redirect after login
* Role-based access control

---

### 🧑‍💼 Admin Panel

* 📤 Upload notes
* ✅ Approve / Reject submissions
* 🗑 Delete notes
* 🔄 Manage user roles (User ↔ Admin)
* 📊 Full platform control

---

### 📊 Advanced Features

* 📈 Download tracking system
* 🏆 Top downloaded notes section
* 📂 Semester-wise organization
* 📱 Fully responsive design
* 🔎 Backend-powered search

---

## 🛠️ Tech Stack

| Category  | Technology                 |
| --------- | -------------------------- |
| Backend   | Python                     |
| Framework | Flask                      |
| Database  | SQLite                     |
| Frontend  | HTML, CSS, JavaScript      |
| Server    | Gunicorn                   |
| Hosting   | Render                     |
| Domain    | GoDaddy                    |
| PWA       | Service Workers + Manifest |

---

## 📂 Project Structure

```
NotesHub/
│── app.py
│── config.py
│── requirements.txt
│
├── database/
│   └── db.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── icons/
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── notes.html
│   └── ...
│
└── uploads/
```

---

## 🌐 Deployment

### 🚀 Render Deployment

Backend is hosted on Render:
👉 https://notes-hub-lpxg.onrender.com

### 🔗 Custom Domain

Connected via GoDaddy:
👉 https://btechnotes.online

---

## ⚙️ Local Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/irahulvashisth01/NotesHub.git
cd NotesHub
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run Application

```bash
python app.py
```

---

## 📱 PWA Support

* Installable on mobile devices
* Add to Home Screen
* Works like a native app
* Fast loading with offline capabilities

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

## 💡 Future Enhancements

* 🔔 Push Notifications
* ⭐ Bookmark / Favorite Notes
* ☁️ Cloud Storage Integration
* 🤖 AI-based Recommendations
* 📊 Advanced Analytics Dashboard

---

## 👨‍💻 Developer

**Rahul Vashisth**
🎓 B.Tech Engineering Student

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
* Authentication & authorization systems
* Admin panel implementation
* Cloud deployment with custom domain
* Progressive Web App (PWA) architecture

💯 **Portfolio-ready & industry-level project**
