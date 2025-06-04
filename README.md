# 🎤 O Estúdio 🎶  
_Stream intimate concerts anytime, anywhere._

Link Demo: https://oestudio-amak.replit.app/

---

## 📖 Overview  
**O Estúdio** is a live concert streaming platform for music lovers. Inspired by Tiny Concerts, it allows users to discover, watch, and engage with exclusive performances from emerging and established artists.

---

## 🚀 Core Features

- 📽 **Stream Live & Recorded Concerts**
- 🔍 **Search & Filter** by Artist, Genre, or Date
- ❤️ **Like, Comment, and Favorite** Videos
- 🎤 **Artist Dashboard** for Content Management
- 🛠 **Admin Panel** for Moderation & Analytics

---

## 🧱 Technology Stack

| Layer       | Stack                                 |
|-------------|----------------------------------------|
| Frontend    | React (Vite)                          |
| Backend     | Flask (Python)                        |
| Forms       | WTForms + Flask-WTF                   |
| Database    | SQLite                                |
| Auth        | JWT (JSON Web Tokens) *(planned)*     |
| CI/CD       | GitHub Actions                        |
| Hosting     | Vercel (Frontend) + Azure (Backend)   |

---

## 🛠 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/o-estudio.git
cd o-estudio

## Backend Setup (Flask)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python main.py

## Frontend Setup (React + Vite)

cd ../react-frontend
npm install
npm run dev

## 📦 Folder Structure
o-estudio/
├── backend/
│   ├── main.py
│   ├── forms.py
│   └── ...
├── frontend/
│   ├── src/
│   ├── public/
│   ├── vite.config.js
│   └── ...



